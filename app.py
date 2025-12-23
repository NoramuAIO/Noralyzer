from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from decimal import Decimal
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'noralyzer-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///noralyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==================== MODELS ====================

class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    holder_name = db.Column(db.String(100))
    iban = db.Column(db.String(34))
    account_type = db.Column(db.String(50)) # Vadesiz TL, Vadeli, Döviz, Altın vb.
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cards = db.relationship('Card', backref='bank', lazy=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    card_type = db.Column(db.String(20))  # credit, debit
    last_four = db.Column(db.String(4))
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    note = db.Column(db.Text)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    category = db.Column(db.String(50))
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7), default='#6c757d')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#17a2b8')


transaction_tags = db.Table('transaction_tags',
    db.Column('transaction_id', db.Integer, db.ForeignKey('transaction.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # TRY, USD, EUR, CAD, BTC, DOGE, GOLD_FULL, GOLD_GRAM, GOLD_QUARTER, CASH
    transaction_type = db.Column(db.String(30), nullable=False)  # atm_withdraw, bank_deposit, card_load, cash_in, cash_out, transfer, crypto_buy, crypto_sell, gold_buy, gold_sell
    description = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)
    time = db.Column(db.String(10))  # HH:MM format
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    from_bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    to_bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('Category', backref='transactions')
    card = db.relationship('Card', backref='transactions')
    bank_ref = db.relationship('Bank', foreign_keys=[bank_id], backref='transactions')
    person = db.relationship('Person', foreign_keys=[person_id], backref='transactions')
    place = db.relationship('Place', backref='transactions')
    from_bank = db.relationship('Bank', foreign_keys=[from_bank_id])
    to_bank = db.relationship('Bank', foreign_keys=[to_bank_id])
    owner = db.relationship('Person', foreign_keys=[owner_id], backref='owned_transactions')
    tags = db.relationship('Tag', secondary=transaction_tags, backref='transactions')

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20))  # weekly, monthly
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    category = db.relationship('Category')

class SavingGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    deadline = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')

class QuickTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10))
    transaction_type = db.Column(db.String(30))
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('Category')
    card = db.relationship('Card')
    bank = db.relationship('Bank')
    person = db.relationship('Person')
    place = db.relationship('Place')

# ==================== CONSTANTS ====================

CURRENCIES = {
    'fiat': ['TRY', 'USD', 'EUR', 'CAD'],
    'crypto': ['BTC', 'DOGE'],
    'gold': ['GOLD_FULL', 'GOLD_GRAM', 'GOLD_QUARTER'],
    'cash': ['CASH_TRY', 'CASH_USD', 'CASH_EUR']
}

CURRENCY_NAMES = {
    'TRY': 'Türk Lirası', 'USD': 'Amerikan Doları', 'EUR': 'Euro', 'CAD': 'Kanada Doları',
    'BTC': 'Bitcoin', 'DOGE': 'Dogecoin',
    'GOLD_FULL': 'Tam Altın', 'GOLD_GRAM': 'Gram Altın', 'GOLD_QUARTER': 'Çeyrek Altın',
    'CASH_TRY': 'Nakit TL', 'CASH_USD': 'Nakit USD', 'CASH_EUR': 'Nakit EUR'
}

TRANSACTION_TYPES = [
    ('atm_withdraw', 'ATM Para Çekme'),
    ('bank_deposit', 'Bankaya Para Yatırma'),
    ('card_load', 'Karta Para Yükleme'),
    ('cash_in', 'Nakit Giriş'),
    ('cash_out', 'Nakit Çıkış'),
    ('transfer', 'Transfer'),
    ('crypto_buy', 'Kripto Alış'),
    ('crypto_sell', 'Kripto Satış'),
    ('crypto_convert', 'Kripto Çevrim'),
    ('gold_buy', 'Altın Alış'),
    ('gold_sell', 'Altın Satış'),
    ('expense', 'Harcama'),
    ('income', 'Gelir')
]

CURRENCY_SYMBOLS = {
    'TRY': '₺', 'USD': '$', 'EUR': '€', 'CAD': 'C$',
    'BTC': '₿', 'DOGE': 'Ð',
    'GOLD_FULL': 'Tam', 'GOLD_GRAM': 'Gr', 'GOLD_QUARTER': 'Çyr',
    'CASH_TRY': '₺', 'CASH_USD': '$', 'CASH_EUR': '€'
}

# ==================== ROUTES ====================

@app.route('/')
def dashboard():
    transactions = Transaction.query.order_by(Transaction.date.desc()).limit(10).all()
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.transaction_type.in_(['income', 'cash_in', 'bank_deposit'])
    ).scalar() or 0
    total_expense = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.transaction_type.in_(['expense', 'cash_out', 'atm_withdraw'])
    ).scalar() or 0
    
    # Category breakdown - convert to plain list for JSON serialization
    category_data_raw = db.session.query(
        Category.name, db.func.sum(Transaction.amount)
    ).join(Transaction).group_by(Category.id).all()
    category_data = [[row[0], float(row[1]) if row[1] else 0] for row in category_data_raw]
    
    budgets = Budget.query.all()
    goals = SavingGoal.query.all()
    
    return render_template('dashboard.html', 
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        category_data=category_data,
        budgets=budgets,
        goals=goals,
        currency_symbols=CURRENCY_SYMBOLS
    )

@app.route('/transactions')
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
        currency_symbols=CURRENCY_SYMBOLS,
        currency_names=CURRENCY_NAMES
    )

@app.route('/transactions/add', methods=['GET', 'POST'])
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
        
        # Tags processing
        if 'tags' in request.form:
             tags = Tag.query.filter(Tag.id.in_(request.form.getlist('tags'))).all()
             transaction.tags.extend(tags)
             
        db.session.add(transaction)
        db.session.commit()
        flash('İşlem eklendi!', 'success')
        return redirect(url_for('transactions'))
        
    return render_template('add_transaction.html',
        transaction_types=TRANSACTION_TYPES,
        currencies=CURRENCIES,
        categories=Category.query.all(),
        banks=Bank.query.all(),
        cards=Card.query.all(),
        persons=Person.query.all(),
        places=Place.query.all(),
        tags=Tag.query.all(),
        quick_transactions=QuickTransaction.query.all(),
        currency_names=CURRENCY_NAMES
    )




@app.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('transactions'))
    
    return render_template('edit_transaction.html',
        transaction=transaction,
        transaction_types=TRANSACTION_TYPES,
        currencies=CURRENCIES,
        categories=Category.query.all(),
        cards=Card.query.all(),
        banks=Bank.query.all(),
        persons=Person.query.all(),
        places=Place.query.all(),
        tags=Tag.query.all(),
        currency_names=CURRENCY_NAMES
    )

@app.route('/transactions/<int:id>/delete', methods=['POST'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem silindi!', 'success')
    return redirect(url_for('transactions'))


# ==================== BANK ROUTES ====================

@app.route('/banks')
def banks():
    banks = Bank.query.order_by(Bank.is_favorite.desc(), Bank.name).all()
    
    # Bank analysis
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

@app.route('/banks/add', methods=['GET', 'POST'])
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
        return redirect(url_for('settings') + '#banks')
    return render_template('add_bank.html')

@app.route('/banks/<int:id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('banks'))
    return render_template('edit_bank.html', bank=bank)

@app.route('/banks/<int:id>/toggle-favorite', methods=['POST'])
def toggle_bank_favorite(id):
    bank = Bank.query.get_or_404(id)
    bank.is_favorite = not bank.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': bank.is_favorite})

@app.route('/banks/<int:id>/delete', methods=['POST'])
def delete_bank(id):
    bank = Bank.query.get_or_404(id)
    db.session.delete(bank)
    db.session.commit()
    flash('Banka silindi!', 'success')
    return redirect(url_for('settings') + '#banks')

# ==================== CARD ROUTES ====================

@app.route('/cards')
def cards():
    cards = Card.query.order_by(Card.is_favorite.desc(), Card.name).all()
    return render_template('cards.html', cards=cards)

@app.route('/cards/add', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        card = Card(
            name=request.form['name'],
            card_type=request.form['card_type'],
            last_four=request.form.get('last_four'),
            bank_id=request.form.get('bank_id') or None,
            is_favorite=bool(request.form.get('is_favorite'))
        )
        db.session.add(card)
        db.session.commit()
        flash('Kart eklendi!', 'success')
        return redirect(url_for('settings') + '#cards')
    return render_template('add_card.html', banks=Bank.query.all())

@app.route('/cards/<int:id>/edit', methods=['GET', 'POST'])
def edit_card(id):
    card = Card.query.get_or_404(id)
    if request.method == 'POST':
        card.name = request.form['name']
        card.card_type = request.form['card_type']
        card.last_four = request.form.get('last_four')
        card.bank_id = request.form.get('bank_id') or None
        card.is_favorite = bool(request.form.get('is_favorite'))
        db.session.commit()
        flash('Kart güncellendi!', 'success')
        return redirect(url_for('cards'))
    return render_template('edit_card.html', card=card, banks=Bank.query.all())

@app.route('/cards/<int:id>/toggle-favorite', methods=['POST'])
def toggle_card_favorite(id):
    card = Card.query.get_or_404(id)
    card.is_favorite = not card.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': card.is_favorite})

@app.route('/cards/<int:id>/delete', methods=['POST'])
def delete_card(id):
    card = Card.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    flash('Kart silindi!', 'success')
    return redirect(url_for('settings') + '#cards')

@app.route('/cards/<int:id>/transactions')
def card_transactions(id):
    card = Card.query.get_or_404(id)
    transactions = Transaction.query.filter_by(card_id=id).order_by(Transaction.date.desc()).all()
    total = sum(t.amount for t in transactions)
    return render_template('card_transactions.html', card=card, transactions=transactions, total=total, currency_symbols=CURRENCY_SYMBOLS)


# ==================== PERSON ROUTES ====================

@app.route('/persons')
def persons():
    persons = Person.query.order_by(Person.is_favorite.desc(), Person.name).all()
    return render_template('persons.html', persons=persons)

@app.route('/persons/add', methods=['GET', 'POST'])
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
        return redirect(url_for('settings') + '#contacts')
    return render_template('add_person.html')

@app.route('/persons/<int:id>/edit', methods=['GET', 'POST'])
def edit_person(id):
    person = Person.query.get_or_404(id)
    if request.method == 'POST':
        person.name = request.form['name']
        person.phone = request.form.get('phone')
        person.note = request.form.get('note')
        person.is_favorite = bool(request.form.get('is_favorite'))
        db.session.commit()
        flash('Kişi güncellendi!', 'success')
        return redirect(url_for('persons'))
    return render_template('edit_person.html', person=person)

@app.route('/persons/<int:id>/toggle-favorite', methods=['POST'])
def toggle_person_favorite(id):
    person = Person.query.get_or_404(id)
    person.is_favorite = not person.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': person.is_favorite})

@app.route('/persons/<int:id>/delete', methods=['POST'])
def delete_person(id):
    person = Person.query.get_or_404(id)
    db.session.delete(person)
    db.session.commit()
    flash('Kişi silindi!', 'success')
    return redirect(url_for('settings') + '#contacts')

@app.route('/persons/<int:id>/report')
def person_report(id):
    person = Person.query.get_or_404(id)
    transactions = Transaction.query.filter_by(person_id=id).order_by(Transaction.date.desc()).all()
    # Sending money TO the person (Expense, Transfer, Cash Out)
    total_sent = sum(t.amount for t in transactions if t.transaction_type in ['expense', 'transfer', 'cash_out'])
    # Receiving money FROM the person (Income, Cash In)
    total_received = sum(t.amount for t in transactions if t.transaction_type in ['income', 'cash_in', 'bank_deposit'])
    return render_template('person_report.html', person=person, transactions=transactions, 
                         total_sent=total_sent, total_received=total_received, currency_symbols=CURRENCY_SYMBOLS)

@app.route('/persons/<int:id>/owner-report')
def owner_report(id):
    """Report for transactions OWNED by this person (i.e. made by this person)"""
    person = Person.query.get_or_404(id)
    transactions = Transaction.query.filter_by(owner_id=id).order_by(Transaction.date.desc()).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type in ['income', 'cash_in', 'bank_deposit'])
    total_expense = sum(t.amount for t in transactions if t.transaction_type in ['expense', 'cash_out', 'atm_withdraw'])
    
    # Category breakdown for owned transactions
    category_breakdown = db.session.query(
        Category.name, Category.icon, db.func.sum(Transaction.amount)
    ).join(Transaction).filter(Transaction.owner_id == id).group_by(Category.id).all()
    
    return render_template('owner_report.html', person=person, transactions=transactions,
                         total_income=total_income, total_expense=total_expense,
                         balance=total_income - total_expense,
                         category_breakdown=category_breakdown, currency_symbols=CURRENCY_SYMBOLS)

# ==================== PLACE ROUTES ====================

@app.route('/places')
def places():
    places = Place.query.order_by(Place.is_favorite.desc(), Place.name).all()
    return render_template('places.html', places=places)

@app.route('/places/add', methods=['GET', 'POST'])
def add_place():
    if request.method == 'POST':
        place = Place(
            name=request.form['name'],
            address=request.form.get('address'),
            category=request.form.get('category'),
            is_favorite=bool(request.form.get('is_favorite'))
        )
        db.session.add(place)
        db.session.commit()
        flash('Yer eklendi!', 'success')
        return redirect(url_for('settings') + '#contacts')
    return render_template('add_place.html')

@app.route('/places/<int:id>/edit', methods=['GET', 'POST'])
def edit_place(id):
    place = Place.query.get_or_404(id)
    if request.method == 'POST':
        place.name = request.form['name']
        place.address = request.form.get('address')
        place.category = request.form.get('category')
        place.is_favorite = bool(request.form.get('is_favorite'))
        db.session.commit()
        flash('Yer güncellendi!', 'success')
        return redirect(url_for('places'))
    return render_template('edit_place.html', place=place)

@app.route('/places/<int:id>/toggle-favorite', methods=['POST'])
def toggle_place_favorite(id):
    place = Place.query.get_or_404(id)
    place.is_favorite = not place.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': place.is_favorite})

@app.route('/places/<int:id>/delete', methods=['POST'])
def delete_place(id):
    place = Place.query.get_or_404(id)
    db.session.delete(place)
    db.session.commit()
    flash('Yer silindi!', 'success')
    return redirect(url_for('settings') + '#contacts')

@app.route('/places/<int:id>/report')
def place_report(id):
    place = Place.query.get_or_404(id)
    transactions = Transaction.query.filter_by(place_id=id).order_by(Transaction.date.desc()).all()
    total_spent = sum(t.amount for t in transactions)
    
    # Category breakdown for this place
    category_breakdown = db.session.query(
        Category.name, db.func.sum(Transaction.amount)
    ).join(Transaction).filter(Transaction.place_id == id).group_by(Category.id).all()
    
    return render_template('place_report.html', place=place, transactions=transactions, 
                         total_spent=total_spent, category_breakdown=category_breakdown, currency_symbols=CURRENCY_SYMBOLS)


# ==================== CATEGORY & TAG ROUTES ====================

@app.route('/categories')
def categories():
    categories = Category.query.all()
    category_stats = []
    for cat in categories:
        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.category_id == cat.id
        ).scalar() or 0
        count = Transaction.query.filter_by(category_id=cat.id).count()
        category_stats.append({'category': cat, 'total': total, 'count': count})
    return render_template('categories.html', category_stats=category_stats)

@app.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category = Category(
            name=request.form['name'],
            icon=request.form.get('icon'),
            color=request.form.get('color', '#6c757d')
        )
        db.session.add(category)
        db.session.commit()
        flash('Kategori eklendi!', 'success')
        return redirect(url_for('settings') + '#categories')
    return render_template('add_category.html')

@app.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        category.icon = request.form.get('icon')
        category.color = request.form.get('color', '#6c757d')
        db.session.commit()
        flash('Kategori güncellendi!', 'success')
        return redirect(url_for('categories'))
    return render_template('edit_category.html', category=category)

@app.route('/categories/<int:id>/delete', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Kategori silindi!', 'success')
    return redirect(url_for('settings') + '#categories')

@app.route('/tags')
def tags():
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)

@app.route('/tags/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        tag = Tag(
            name=request.form['name'],
            color=request.form.get('color', '#17a2b8')
        )
        db.session.add(tag)
        db.session.commit()
        flash('Etiket eklendi!', 'success')
        return redirect(url_for('settings') + '#tags')
    return render_template('add_tag.html')

@app.route('/tags/<int:id>/delete', methods=['POST'])
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('Etiket silindi!', 'success')
    return redirect(url_for('settings') + '#tags')

# ==================== BUDGET & GOALS ROUTES ====================

@app.route('/budgets')
def budgets():
    budgets = Budget.query.all()
    budget_stats = []
    for budget in budgets:
        if budget.category_id:
            spent = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.category_id == budget.category_id,
                Transaction.date >= budget.start_date if budget.start_date else True,
                Transaction.date <= budget.end_date if budget.end_date else True
            ).scalar() or 0
        else:
            spent = 0
        remaining = budget.amount - spent
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        budget_stats.append({'budget': budget, 'spent': spent, 'remaining': remaining, 'percentage': min(percentage, 100)})
    return render_template('budgets.html', budget_stats=budget_stats)

@app.route('/budgets/add', methods=['GET', 'POST'])
def add_budget():
    if request.method == 'POST':
        budget = Budget(
            name=request.form['name'],
            amount=float(request.form['amount']),
            period=request.form.get('period'),
            category_id=request.form.get('category_id') or None,
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form.get('start_date') else None,
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None
        )
        db.session.add(budget)
        db.session.commit()
        flash('Bütçe eklendi!', 'success')
        return redirect(url_for('settings') + '#budgets')
    return render_template('add_budget.html', categories=Category.query.all())

@app.route('/budgets/<int:id>/delete', methods=['POST'])
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    db.session.delete(budget)
    db.session.commit()
    flash('Bütçe silindi!', 'success')
    return redirect(url_for('settings') + '#budgets')

@app.route('/goals')
def goals():
    goals = SavingGoal.query.all()
    goal_stats = []
    
    for goal in goals:
        current_amount = float(goal.current_amount) # Manual amount as base
        
        # If category is linked, sum up relevant transactions
        if goal.category_id:
            # Sum income/savings related transactions for this category
            # We assume savings are marked with this category and income type
            category_savings = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.category_id == goal.category_id,
                Transaction.transaction_type.in_(['income', 'cash_in', 'bank_deposit']) 
            ).scalar() or 0
            current_amount += float(category_savings)
            
        percentage = (current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        remaining = goal.target_amount - current_amount
        
        # Dynamic object to pass to template without modifying DB object permanently in this view
        goal_display = {
            'id': goal.id,
            'name': goal.name,
            'target_amount': goal.target_amount,
            'current_amount': current_amount,
            'deadline': goal.deadline,
            'category': goal.category
        }
        
        goal_stats.append({'goal': goal_display, 'percentage': min(percentage, 100), 'remaining': remaining})
    return render_template('goals.html', goal_stats=goal_stats)

@app.route('/goals/add', methods=['GET', 'POST'])
def add_goal():
    if request.method == 'POST':
        goal = SavingGoal(
            name=request.form['name'],
            target_amount=float(request.form['target_amount']),
            current_amount=float(request.form.get('current_amount', 0)),
            deadline=datetime.strptime(request.form['deadline'], '%Y-%m-%d').date() if request.form.get('deadline') else None
        )
        if request.form.get('category_id'):
            goal.category_id = int(request.form['category_id'])
            
        db.session.add(goal)
        db.session.commit()
        flash('Hedef eklendi!', 'success')
        return redirect(url_for('goals'))
    return render_template('add_goal.html', categories=Category.query.all())

@app.route('/goals/<int:id>/update', methods=['POST'])
def update_goal(id):
    # Bu metod artık kullanılmıyor, hedefler otomatik hesaplanıyor
    return redirect(url_for('goals'))

@app.route('/goals/<int:id>/delete', methods=['POST'])
def delete_goal(id):
    goal = SavingGoal.query.get_or_404(id)
    db.session.delete(goal)
    db.session.commit()
    flash('Hedef silindi!', 'success')
    return redirect(url_for('goals'))




# ==================== QUICK TRANSACTION ROUTES ====================

@app.route('/quick-transactions')
def quick_transactions():
    quick_txs = QuickTransaction.query.all()
    return render_template('quick_transactions.html', quick_transactions=quick_txs)

@app.route('/quick-transactions/add', methods=['GET', 'POST'])
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
        return redirect(url_for('quick_transactions'))
    return render_template('add_quick_transaction.html',
        transaction_types=TRANSACTION_TYPES,
        currencies=CURRENCIES,
        categories=Category.query.all(),
        cards=Card.query.all(),
        banks=Bank.query.all(),
        persons=Person.query.all(),
        places=Place.query.all()
    )

@app.route('/quick-transactions/<int:id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('quick_transactions'))
    return render_template('edit_quick_transaction.html',
        qt=qt,
        transaction_types=TRANSACTION_TYPES,
        currencies=CURRENCIES,
        categories=Category.query.all(),
        cards=Card.query.all(),
        banks=Bank.query.all(),
        persons=Person.query.all(),
        places=Place.query.all()
    )

@app.route('/quick-transactions/<int:id>/use', methods=['POST'])
def use_quick_transaction(id):
    qt = QuickTransaction.query.get_or_404(id)
    # Verileri query parameter olarak add_transaction sayfasına taşı
    return redirect(url_for('add_transaction', 
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

@app.route('/quick-transactions/<int:id>/delete', methods=['POST'])
def delete_quick_transaction(id):
    qt = QuickTransaction.query.get_or_404(id)
    db.session.delete(qt)
    db.session.commit()
    flash('Hızlı işlem şablonu silindi!', 'success')
    return redirect(url_for('quick_transactions'))

# ==================== SETTINGS ROUTES ====================

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)

def get_settings():
    settings = {}
    for s in Setting.query.all():
        settings[s.key] = s.value
    return settings

def save_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.session.add(setting)
    db.session.commit()

@app.route('/settings')
def settings():
    # Budget stats for settings page
    budgets_list = Budget.query.all()
    budget_stats = []
    for budget in budgets_list:
        if budget.category_id:
            spent = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.category_id == budget.category_id
            ).scalar() or 0
        else:
            spent = 0
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        budget_stats.append({'budget': budget, 'spent': spent, 'percentage': min(percentage, 100)})
    
    return render_template('settings.html',
        settings=get_settings(),
        banks=Bank.query.order_by(Bank.is_favorite.desc(), Bank.name).all(),
        cards=Card.query.order_by(Card.is_favorite.desc(), Card.name).all(),
        persons=Person.query.order_by(Person.is_favorite.desc(), Person.name).all(),
        places=Place.query.order_by(Place.is_favorite.desc(), Place.name).all(),
        categories=Category.query.all(),
        tags=Tag.query.all(),
        budget_stats=budget_stats
    )

@app.route('/settings/save', methods=['POST'])
def save_settings():
    section = request.form.get('section')
    
    if section == 'general':
        save_setting('app_name', request.form.get('app_name', 'Noralyzer'))
        save_setting('default_currency', request.form.get('default_currency', 'TRY'))
        save_setting('date_format', request.form.get('date_format', 'DD.MM.YYYY'))
        save_setting('items_per_page', request.form.get('items_per_page', '20'))
    elif section == 'appearance':
        save_setting('theme', request.form.get('theme', 'dark'))
        save_setting('primary_color', request.form.get('primary_color', '#6366f1'))
        save_setting('compact_mode', 'true' if request.form.get('compact_mode') else 'false')
    elif section == 'notifications':
        save_setting('budget_alerts', 'true' if request.form.get('budget_alerts') else 'false')
        save_setting('goal_reminders', 'true' if request.form.get('goal_reminders') else 'false')
        save_setting('weekly_summary', 'true' if request.form.get('weekly_summary') else 'false')
    elif section == 'currencies':
        currencies = request.form.getlist('currencies')
        save_setting('active_currencies', ','.join(currencies))
    
    flash('Ayarlar kaydedildi!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/export')
def export_data():
    data = {
        'banks': [{'name': b.name, 'holder_name': b.holder_name, 'iban': b.iban} for b in Bank.query.all()],
        'cards': [{'name': c.name, 'card_type': c.card_type, 'last_four': c.last_four} for c in Card.query.all()],
        'persons': [{'name': p.name, 'phone': p.phone, 'note': p.note} for p in Person.query.all()],
        'places': [{'name': p.name, 'address': p.address, 'category': p.category} for p in Place.query.all()],
        'categories': [{'name': c.name, 'icon': c.icon, 'color': c.color} for c in Category.query.all()],
        'tags': [{'name': t.name, 'color': t.color} for t in Tag.query.all()],
        'transactions': [{
            'amount': t.amount, 'currency': t.currency, 'transaction_type': t.transaction_type,
            'description': t.description, 'date': t.date.isoformat() if t.date else None
        } for t in Transaction.query.all()]
    }
    response = app.response_class(
        response=json.dumps(data, ensure_ascii=False, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=noralyzer_backup.json'}
    )
    return response

@app.route('/settings/import', methods=['POST'])
def import_data():
    if 'file' not in request.files:
        flash('Dosya seçilmedi!', 'danger')
        return redirect(url_for('settings'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Dosya seçilmedi!', 'danger')
        return redirect(url_for('settings'))
    
    try:
        data = json.load(file)
        
        for cat in data.get('categories', []):
            if not Category.query.filter_by(name=cat['name']).first():
                db.session.add(Category(name=cat['name'], icon=cat.get('icon'), color=cat.get('color')))
        
        for tag in data.get('tags', []):
            if not Tag.query.filter_by(name=tag['name']).first():
                db.session.add(Tag(name=tag['name'], color=tag.get('color')))
        
        for bank in data.get('banks', []):
            if not Bank.query.filter_by(name=bank['name']).first():
                db.session.add(Bank(name=bank['name'], holder_name=bank.get('holder_name'), iban=bank.get('iban')))
        
        db.session.commit()
        flash('Veriler başarıyla içe aktarıldı!', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('settings'))

@app.route('/settings/delete-all-transactions', methods=['POST'])
def delete_all_transactions():
    Transaction.query.delete()
    db.session.commit()
    flash('Tüm işlemler silindi!', 'success')
    return redirect(url_for('settings') + '#danger')

@app.route('/settings/reset-database', methods=['POST'])
def reset_database():
    db.drop_all()
    db.create_all()
    init_db()
    flash('Veritabanı sıfırlandı!', 'success')
    return redirect(url_for('settings'))

# ==================== REPORTS & ANALYTICS ====================

from datetime import timedelta
from dateutil.relativedelta import relativedelta

@app.route('/reports')
def reports():
    date_range = request.args.get('range', '6m')
    category_id = request.args.get('category')
    today = date.today()
    start_date = None
    
    if date_range == '6m':
        start_date = today - relativedelta(months=6)
    elif date_range == '12m':
        start_date = today - relativedelta(months=12)
    elif date_range == 'custom':
        custom_start = request.args.get('start_date')
        if custom_start:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()

    # Query Filters
    query = Transaction.query
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    # Category filter
    current_category = None
    if category_id:
        if category_id == 'uncategorized':
            current_category = type('obj', (object,), {'name': 'Kategorisiz', 'icon': '<i class="bi bi-question-circle"></i>'})
            query = query.filter(Transaction.category_id == None)
        else:
            current_category = Category.query.get(category_id)
            query = query.filter(Transaction.category_id == category_id)

    transactions = query.all()

    # Calculate Totals
    total_income = sum(t.amount for t in transactions if t.transaction_type in ['income', 'cash_in', 'bank_deposit'])
    total_expense = sum(t.amount for t in transactions if t.transaction_type in ['expense', 'cash_out', 'atm_withdraw'])
    
    # Category Stats
    category_totals = {}
    for t in transactions:
        if t.transaction_type in ['expense', 'cash_out', 'atm_withdraw'] and t.category:
            if t.category not in category_totals:
                category_totals[t.category] = 0
            category_totals[t.category] += t.amount
    
    category_stats = []
    for cat, total in category_totals.items():
        category_stats.append({
            'category': cat,
            'total': total,
            'percentage': (total / total_expense * 100) if total_expense > 0 else 0
        })
    category_stats.sort(key=lambda x: x['total'], reverse=True)

    # Monthly Trend Data (Chart)
    monthly_data = {}
    for t in transactions:
        month_key = t.date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        
        if t.transaction_type in ['income', 'cash_in', 'bank_deposit']:
            monthly_data[month_key]['income'] += t.amount
        elif t.transaction_type in ['expense', 'cash_out', 'atm_withdraw']:
            monthly_data[month_key]['expense'] += t.amount
    
    # Create labels with readable month names
    month_names = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                   'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    
    months = sorted(monthly_data.keys())
    readable_labels = []
    for m in months:
        year, month = m.split('-')
        month_idx = int(month) - 1
        readable_labels.append(f"{month_names[month_idx]} {year}")
    
    chart_data = {
        'labels': readable_labels,
        'income': [monthly_data[m]['income'] for m in months],
        'expense': [monthly_data[m]['expense'] for m in months]
    }
    
    return render_template('reports.html', 
                          total_income=total_income, 
                          total_expense=total_expense,
                          category_stats=category_stats,
                          chart_data=chart_data,
                          current_range=date_range,
                          current_category=current_category,
                          categories=Category.query.all())

@app.route('/api/chart-data')
def chart_data_api():
    # Monthly spending trend (Last 6 months)
    start_date = date.today() - relativedelta(months=6)
    monthly_data = db.session.query(
        db.func.strftime('%Y-%m', Transaction.date),
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.transaction_type.in_(['expense', 'cash_out', 'atm_withdraw']),
        Transaction.date >= start_date
    ).group_by(
        db.func.strftime('%Y-%m', Transaction.date)
    ).order_by(db.func.strftime('%Y-%m', Transaction.date)).all()
    
    # Category breakdown (All time)
    category_data = db.session.query(
        Category.name, db.func.sum(Transaction.amount)
    ).join(Transaction).filter(
        Transaction.transaction_type.in_(['expense', 'cash_out', 'atm_withdraw'])
    ).group_by(Category.id).all()
    
    return jsonify({
        'monthly': {'labels': [m[0] for m in monthly_data], 'data': [float(m[1] or 0) for m in monthly_data]},
        'categories': {'labels': [c[0] for c in category_data], 'data': [float(c[1] or 0) for c in category_data]}
    })

# ==================== INIT ====================

def init_db():
    with app.app_context():
        db.create_all()
        # Add default categories if empty
        if Category.query.count() == 0:
            default_categories = [
                ('Yemek', '🍔', '#e74c3c'),
                ('Ulaşım', '🚗', '#3498db'),
                ('Kira', '🏠', '#9b59b6'),
                ('Eğlence', '🎮', '#f39c12'),
                ('Sağlık', '💊', '#1abc9c'),
                ('Giyim', '👕', '#e91e63'),
                ('Faturalar', '📄', '#607d8b'),
                ('Market', '🛒', '#4caf50'),
                ('Diğer', '📦', '#95a5a6')
            ]
            for name, icon, color in default_categories:
                db.session.add(Category(name=name, icon=icon, color=color))
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
