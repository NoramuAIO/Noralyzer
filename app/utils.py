from app import db
from app.models import Currency, TransactionType, DefaultCategory, Category

def get_currencies():
    """Para birimlerini tipine göre grupla"""
    currencies = Currency.query.filter_by(is_active=True).all()
    result = {'fiat': [], 'crypto': [], 'gold': [], 'cash': []}
    for c in currencies:
        if c.currency_type in result:
            result[c.currency_type].append(c.code)
    return result

def get_currency_names():
    """Para birimi isimlerini getir"""
    currencies = Currency.query.all()
    return {c.code: c.name for c in currencies}

def get_currency_symbols():
    """Para birimi sembollerini getir"""
    currencies = Currency.query.all()
    return {c.code: c.symbol for c in currencies}

def get_transaction_types():
    """İşlem tiplerini tuple listesi olarak getir"""
    types = TransactionType.query.filter_by(is_active=True).all()
    return [(t.code, t.name) for t in types]

def init_default_data():
    """Varsayılan verileri veritabanına yükle"""
    
    # Para birimleri
    default_currencies = [
        ('TRY', 'Türk Lirası', '₺', 'fiat'),
        ('USD', 'Amerikan Doları', '$', 'fiat'),
        ('EUR', 'Euro', '€', 'fiat'),
        ('CAD', 'Kanada Doları', 'C$', 'fiat'),
        ('BTC', 'Bitcoin', '₿', 'crypto'),
        ('DOGE', 'Dogecoin', 'Ð', 'crypto'),
        ('GOLD_FULL', 'Tam Altın', 'Tam', 'gold'),
        ('GOLD_GRAM', 'Gram Altın', 'Gr', 'gold'),
        ('GOLD_QUARTER', 'Çeyrek Altın', 'Çyr', 'gold'),
        ('CASH_TRY', 'Nakit TL', '₺', 'cash'),
        ('CASH_USD', 'Nakit USD', '$', 'cash'),
        ('CASH_EUR', 'Nakit EUR', '€', 'cash'),
    ]
    
    if Currency.query.count() == 0:
        for code, name, symbol, ctype in default_currencies:
            db.session.add(Currency(code=code, name=name, symbol=symbol, currency_type=ctype))
    
    # İşlem tipleri
    default_types = [
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
        ('income', 'Gelir'),
    ]
    
    if TransactionType.query.count() == 0:
        for code, name in default_types:
            db.session.add(TransactionType(code=code, name=name))
    
    # Varsayılan kategoriler
    default_categories = [
        ('Yemek', '🍔', '#e74c3c'),
        ('Ulaşım', '🚗', '#3498db'),
        ('Kira', '🏠', '#9b59b6'),
        ('Eğlence', '🎮', '#f39c12'),
        ('Sağlık', '💊', '#1abc9c'),
        ('Giyim', '👕', '#e91e63'),
        ('Faturalar', '📄', '#607d8b'),
        ('Market', '🛒', '#4caf50'),
        ('Diğer', '📦', '#95a5a6'),
    ]
    
    if Category.query.count() == 0:
        for name, icon, color in default_categories:
            db.session.add(Category(name=name, icon=icon, color=color))
    
    db.session.commit()
