from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Transaction, Category, Budget, SavingGoal, Bank, Card, Person, Place, Tag, Setting
from app.utils import get_currency_symbols, init_default_data
import json

main_bp = Blueprint('main', __name__)

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

@main_bp.route('/')
def dashboard():
    transactions = Transaction.query.order_by(Transaction.date.desc()).limit(10).all()
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.transaction_type.in_(['income', 'cash_in', 'bank_deposit'])
    ).scalar() or 0
    total_expense = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.transaction_type.in_(['expense', 'cash_out', 'atm_withdraw'])
    ).scalar() or 0
    
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
        currency_symbols=get_currency_symbols()
    )

@main_bp.route('/settings')
def settings():
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


@main_bp.route('/settings/save', methods=['POST'])
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
    return redirect(url_for('main.settings'))

@main_bp.route('/settings/export')
def export_data():
    from app.models import Bank, Card, Person, Place, Category, Tag, Transaction
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
    from flask import current_app
    response = current_app.response_class(
        response=json.dumps(data, ensure_ascii=False, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=noralyzer_backup.json'}
    )
    return response

@main_bp.route('/settings/import', methods=['POST'])
def import_data():
    from app.models import Bank, Card, Person, Place, Category, Tag
    if 'file' not in request.files:
        flash('Dosya seçilmedi!', 'danger')
        return redirect(url_for('main.settings'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Dosya seçilmedi!', 'danger')
        return redirect(url_for('main.settings'))
    
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
    
    return redirect(url_for('main.settings'))

@main_bp.route('/settings/delete-all-transactions', methods=['POST'])
def delete_all_transactions():
    Transaction.query.delete()
    db.session.commit()
    flash('Tüm işlemler silindi!', 'success')
    return redirect(url_for('main.settings') + '#danger')

@main_bp.route('/settings/reset-database', methods=['POST'])
def reset_database():
    db.drop_all()
    db.create_all()
    init_default_data()
    flash('Veritabanı sıfırlandı!', 'success')
    return redirect(url_for('main.settings'))
