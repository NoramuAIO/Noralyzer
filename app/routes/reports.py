from flask import Blueprint, render_template, request, jsonify
from datetime import date
from dateutil.relativedelta import relativedelta
from app import db
from app.models import Transaction, Category

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
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
            from datetime import datetime
            start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()

    query = Transaction.query
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    current_category = None
    if category_id:
        if category_id == 'uncategorized':
            current_category = type('obj', (object,), {'name': 'Kategorisiz', 'icon': '<i class="bi bi-question-circle"></i>'})
            query = query.filter(Transaction.category_id == None)
        else:
            current_category = Category.query.get(category_id)
            query = query.filter(Transaction.category_id == category_id)

    transactions = query.all()

    total_income = sum(t.amount for t in transactions if t.transaction_type in ['income', 'cash_in', 'bank_deposit'])
    total_expense = sum(t.amount for t in transactions if t.transaction_type in ['expense', 'cash_out', 'atm_withdraw'])
    
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

    monthly_data = {}
    for t in transactions:
        month_key = t.date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        
        if t.transaction_type in ['income', 'cash_in', 'bank_deposit']:
            monthly_data[month_key]['income'] += t.amount
        elif t.transaction_type in ['expense', 'cash_out', 'atm_withdraw']:
            monthly_data[month_key]['expense'] += t.amount
    
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

@reports_bp.route('/api/chart-data')
def chart_data_api():
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
    
    category_data = db.session.query(
        Category.name, db.func.sum(Transaction.amount)
    ).join(Transaction).filter(
        Transaction.transaction_type.in_(['expense', 'cash_out', 'atm_withdraw'])
    ).group_by(Category.id).all()
    
    return jsonify({
        'monthly': {'labels': [m[0] for m in monthly_data], 'data': [float(m[1] or 0) for m in monthly_data]},
        'categories': {'labels': [c[0] for c in category_data], 'data': [float(c[1] or 0) for c in category_data]}
    })
