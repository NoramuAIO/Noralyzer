from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Person, Transaction, Category
from app.utils import get_currency_symbols

persons_bp = Blueprint('persons', __name__)

@persons_bp.route('/persons')
def persons():
    persons = Person.query.order_by(Person.is_favorite.desc(), Person.name).all()
    return render_template('persons.html', persons=persons)

@persons_bp.route('/persons/add', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        person = Person(
            name=request.form['name'],
            phone=request.form.get('phone'),
            note=request.form.get('note'),
            is_favorite=bool(request.form.get('is_favorite'))
        )
        db.session.add(person)
        db.session.commit()
        flash('Kişi eklendi!', 'success')
        return redirect(url_for('main.settings') + '#contacts')
    return render_template('add_person.html')

@persons_bp.route('/persons/<int:id>/edit', methods=['GET', 'POST'])
def edit_person(id):
    person = Person.query.get_or_404(id)
    if request.method == 'POST':
        person.name = request.form['name']
        person.phone = request.form.get('phone')
        person.note = request.form.get('note')
        person.is_favorite = bool(request.form.get('is_favorite'))
        db.session.commit()
        flash('Kişi güncellendi!', 'success')
        return redirect(url_for('persons.persons'))
    return render_template('edit_person.html', person=person)

@persons_bp.route('/persons/<int:id>/toggle-favorite', methods=['POST'])
def toggle_person_favorite(id):
    person = Person.query.get_or_404(id)
    person.is_favorite = not person.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': person.is_favorite})

@persons_bp.route('/persons/<int:id>/delete', methods=['POST'])
def delete_person(id):
    person = Person.query.get_or_404(id)
    db.session.delete(person)
    db.session.commit()
    flash('Kişi silindi!', 'success')
    return redirect(url_for('main.settings') + '#contacts')

@persons_bp.route('/persons/<int:id>/report')
def person_report(id):
    person = Person.query.get_or_404(id)
    transactions = Transaction.query.filter_by(person_id=id).order_by(Transaction.date.desc()).all()
    total_sent = sum(t.amount for t in transactions if t.transaction_type in ['expense', 'transfer', 'cash_out'])
    total_received = sum(t.amount for t in transactions if t.transaction_type in ['income', 'cash_in', 'bank_deposit'])
    return render_template('person_report.html', person=person, transactions=transactions, 
                         total_sent=total_sent, total_received=total_received, currency_symbols=get_currency_symbols())

@persons_bp.route('/persons/<int:id>/owner-report')
def owner_report(id):
    person = Person.query.get_or_404(id)
    transactions = Transaction.query.filter_by(owner_id=id).order_by(Transaction.date.desc()).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type in ['income', 'cash_in', 'bank_deposit'])
    total_expense = sum(t.amount for t in transactions if t.transaction_type in ['expense', 'cash_out', 'atm_withdraw'])
    
    category_breakdown = db.session.query(
        Category.name, Category.icon, db.func.sum(Transaction.amount)
    ).join(Transaction).filter(Transaction.owner_id == id).group_by(Category.id).all()
    
    return render_template('owner_report.html', person=person, transactions=transactions,
                         total_income=total_income, total_expense=total_expense,
                         balance=total_income - total_expense,
                         category_breakdown=category_breakdown, currency_symbols=get_currency_symbols())
