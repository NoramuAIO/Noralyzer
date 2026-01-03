from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Bank, Transaction

banks_bp = Blueprint('banks', __name__)

@banks_bp.route('/banks')
def banks():
    banks = Bank.query.order_by(Bank.is_favorite.desc(), Bank.name).all()
    bank_stats = []
    for bank in banks:
        income = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.bank_id == bank.id,
            Transaction.transaction_type.in_(['income', 'bank_deposit', 'transfer'])
        ).scalar() or 0
        expense = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.bank_id == bank.id,
            Transaction.transaction_type.in_(['expense', 'atm_withdraw', 'cash_out'])
        ).scalar() or 0
        bank_stats.append({'bank': bank, 'income': income, 'expense': expense, 'balance': income - expense})
    return render_template('banks.html', bank_stats=bank_stats)

@banks_bp.route('/banks/add', methods=['GET', 'POST'])
def add_bank():
    if request.method == 'POST':
        bank = Bank(
            name=request.form['name'],
            holder_name=request.form.get('holder_name'),
            iban=request.form.get('iban'),
            account_type=request.form.get('account_type'),
            is_favorite=bool(request.form.get('is_favorite'))
        )
        db.session.add(bank)
        db.session.commit()
        flash('Banka eklendi!', 'success')
        return redirect(url_for('main.settings') + '#banks')
    return render_template('add_bank.html')

@banks_bp.route('/banks/<int:id>/edit', methods=['GET', 'POST'])
def edit_bank(id):
    bank = Bank.query.get_or_404(id)
    if request.method == 'POST':
        bank.name = request.form['name']
        bank.holder_name = request.form.get('holder_name')
        bank.iban = request.form.get('iban')
        bank.account_type = request.form.get('account_type')
        bank.is_favorite = bool(request.form.get('is_favorite'))
        db.session.commit()
        flash('Banka güncellendi!', 'success')
        return redirect(url_for('banks.banks'))
    return render_template('edit_bank.html', bank=bank)

@banks_bp.route('/banks/<int:id>/toggle-favorite', methods=['POST'])
def toggle_bank_favorite(id):
    bank = Bank.query.get_or_404(id)
    bank.is_favorite = not bank.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': bank.is_favorite})

@banks_bp.route('/banks/<int:id>/delete', methods=['POST'])
def delete_bank(id):
    bank = Bank.query.get_or_404(id)
    db.session.delete(bank)
    db.session.commit()
    flash('Banka silindi!', 'success')
    return redirect(url_for('main.settings') + '#banks')
