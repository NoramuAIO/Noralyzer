from app import db
from datetime import datetime, date

class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    holder_name = db.Column(db.String(100))
    iban = db.Column(db.String(34))
    account_type = db.Column(db.String(50))
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cards = db.relationship('Card', backref='bank', lazy=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    card_type = db.Column(db.String(20))
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
    currency = db.Column(db.String(10), nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)
    time = db.Column(db.String(10))
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
    period = db.Column(db.String(20))
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

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)

# ==================== CURRENCY & TRANSACTION TYPE MODELS ====================

class Currency(db.Model):
    """Para birimi modeli"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # TRY, USD, BTC
    name = db.Column(db.String(50), nullable=False)  # Türk Lirası
    symbol = db.Column(db.String(10), nullable=False)  # ₺
    currency_type = db.Column(db.String(20), nullable=False)  # fiat, crypto, gold, cash
    is_active = db.Column(db.Boolean, default=True)

class TransactionType(db.Model):
    """İşlem tipi modeli"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)  # expense, income
    name = db.Column(db.String(50), nullable=False)  # Harcama, Gelir
    is_active = db.Column(db.Boolean, default=True)

class DefaultCategory(db.Model):
    """Varsayılan kategori şablonları"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7), default='#6c757d')
