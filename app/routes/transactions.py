from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from app import db
from app.models import Transaction, Category, Bank, Card, Person, Place, Tag, QuickTransaction
from app.utils import get_currencies, get_currency_symbols, get_currency_names, get_transaction_types

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
def transactions():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category')
    person_id = request.args.get('person')
    owner_id = request.args.get('owner')
    place_id = request.args.get('place')
    card_id = request.args.get('card')
    bank_id = request.args.get('bank')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Transaction.query
    
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if person_id:
        query = query.filter(Transaction.person_id == person_id)
    if owner_id:
        query = query.filter(Transaction.owner_id == owner_id)
    if place_id:
        query = query.filter(Transaction.place_id == place_id)
    if card_id:
        query = query.filter(Transaction.card_id == card_id)
    if bank_id:
        query = query.filter(Transaction.bank_id == bank_id)
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    
    transactions = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=20)
    
    return render_template('transactions.html',
        transactions=transactions,
        categories=Category.query.all(),
        persons=Person.query.all(),
        places=Place.query.all(),
        cards=Card.query.all(),
        banks=Bank.query.all(),
        currency_symbols=get_currency_symbols(),
        currency_names=get_currency_names()
    )

@transactions_bp.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        transaction = Transaction(
            amount=float(request.form['amount']),
            currency=request.form['currency'],
            transaction_type=request.form['transaction_type'],
            description=request.form.get('description'),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date() if request.form.get('date') else date.today(),
            time=request.form.get('time') or None,
            category_id=request.form.get('category_id') or None,
            card_id=request.form.get('card_id') or None,
            bank_id=request.form.get('bank_id') or None,
            person_id=request.form.get('person_id') or None,
            owner_id=request.form.get('owner_id') or None,
            place_id=request.form.get('place_id') or None,
            from_bank_id=request.form.get('from_bank_id') or None,
            to_bank_id=request.form.get('to_bank_id') or None
        )
        
        if 'tags' in request.form:
             tags = Tag.query.filter(Tag.id.in_(request.form.getlist('tags'))).all()
             transaction.tags.extend(tags)
             
        db.session.add(transaction)
        db.session.commit()
        flash('İşlem eklendi!', 'success')
        return redirect(url_for('transactions.transactions'))
        
    return render_template('add_transaction.html',
        transaction_types=get_transaction_types(),
        currencies=get_currencies(),
        categories=Category.query.all(),
        banks=Bank.query.all(),
        cards=Card.query.all(),
        persons=Person.query.all(),
        places=Place.query.all(),
        tags=Tag.query.all(),
        quick_transactions=QuickTransaction.query.all(),
        currency_names=get_currency_names()
    )


@transactions_bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if request.method == 'POST':
        transaction.amount = float(request.form['amount'])
        transaction.currency = request.form['currency']
        transaction.transaction_type = request.form['transaction_type']
        transaction.description = request.form.get('description')
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date() if request.form.get('date') else transaction.date
        transaction.time = request.form.get('time') or None
        transaction.category_id = request.form.get('category_id') or None
        transaction.card_id = request.form.get('card_id') or None
        transaction.bank_id = request.form.get('bank_id') or None
        transaction.person_id = request.form.get('person_id') or None
        transaction.owner_id = request.form.get('owner_id') or None
        transaction.place_id = request.form.get('place_id') or None
        
        db.session.commit()
        flash('İşlem güncellendi!', 'success')
        return redirect(url_for('transactions.transactions'))
    
    return render_template('edit_transaction.html',
        transaction=transaction,
        transaction_types=get_transaction_types(),
        currencies=get_currencies(),
        categories=Category.query.all(),
        cards=Card.query.all(),
        banks=Bank.query.all(),
        persons=Person.query.all(),
        places=Place.query.all(),
        tags=Tag.query.all(),
        currency_names=get_currency_names()
    )

@transactions_bp.route('/transactions/<int:id>/delete', methods=['POST'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem silindi!', 'success')
    return redirect(url_for('transactions.transactions'))

# Quick Transactions
@transactions_bp.route('/quick-transactions')
def quick_transactions():
    quick_txs = QuickTransaction.query.all()
    return render_template('quick_transactions.html', quick_transactions=quick_txs)

@transactions_bp.route('/quick-transactions/add', methods=['GET', 'POST'])
def add_quick_transaction():
    if request.method == 'POST':
        qt = QuickTransaction(
            name=request.form['name'],
            amount=float(request.form['amount']) if request.form.get('amount') else None,
            currency=request.form.get('currency'),
            transaction_type=request.form.get('transaction_type'),
            description=request.form.get('description'),
            category_id=request.form.get('category_id') or None,
            card_id=request.form.get('card_id') or None,
            bank_id=request.form.get('bank_id') or None,
            person_id=request.form.get('person_id') or None,
            place_id=request.form.get('place_id') or None
        )
        db.session.add(qt)
        db.session.commit()
        flash('Hızlı işlem şablonu eklendi!', 'success')
        return redirect(url_for('transactions.quick_transactions'))
    return render_template('add_quick_transaction.html',
        transaction_types=get_transaction_types(),
        currencies=get_currencies(),
        categories=Category.query.all(),
        cards=Card.query.all(),
        banks=Bank.query.all(),
        persons=Person.query.all(),
        places=Place.query.all()
    )

@transactions_bp.route('/quick-transactions/<int:id>/edit', methods=['GET', 'POST'])
def edit_quick_transaction(id):
    qt = QuickTransaction.query.get_or_404(id)
    if request.method == 'POST':
        qt.name = request.form['name']
        qt.amount = float(request.form['amount']) if request.form.get('amount') else None
        qt.currency = request.form.get('currency')
        qt.transaction_type = request.form.get('transaction_type')
        qt.description = request.form.get('description')
        qt.category_id = request.form.get('category_id') or None
        qt.card_id = request.form.get('card_id') or None
        qt.bank_id = request.form.get('bank_id') or None
        qt.person_id = request.form.get('person_id') or None
        qt.place_id = request.form.get('place_id') or None
        db.session.commit()
        flash('Hızlı işlem şablonu güncellendi!', 'success')
        return redirect(url_for('transactions.quick_transactions'))
    return render_template('edit_quick_transaction.html',
        qt=qt,
        transaction_types=get_transaction_types(),
        currencies=get_currencies(),
        categories=Category.query.all(),
        cards=Card.query.all(),
        banks=Bank.query.all(),
        persons=Person.query.all(),
        places=Place.query.all()
    )

@transactions_bp.route('/quick-transactions/<int:id>/use', methods=['POST'])
def use_quick_transaction(id):
    qt = QuickTransaction.query.get_or_404(id)
    return redirect(url_for('transactions.add_transaction', 
        amount=qt.amount,
        currency=qt.currency,
        transaction_type=qt.transaction_type,
        description=qt.description,
        category_id=qt.category_id,
        card_id=qt.card_id,
        bank_id=qt.bank_id,
        person_id=qt.person_id,
        place_id=qt.place_id
    ))

@transactions_bp.route('/quick-transactions/<int:id>/delete', methods=['POST'])
def delete_quick_transaction(id):
    qt = QuickTransaction.query.get_or_404(id)
    db.session.delete(qt)
    db.session.commit()
    flash('Hızlı işlem şablonu silindi!', 'success')
    return redirect(url_for('transactions.quick_transactions'))
