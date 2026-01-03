from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app import db
from app.models import Budget, SavingGoal, Category, Transaction

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/budgets')
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

@budgets_bp.route('/budgets/add', methods=['GET', 'POST'])
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
        return redirect(url_for('main.settings') + '#budgets')
    return render_template('add_budget.html', categories=Category.query.all())

@budgets_bp.route('/budgets/<int:id>/delete', methods=['POST'])
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    db.session.delete(budget)
    db.session.commit()
    flash('Bütçe silindi!', 'success')
    return redirect(url_for('main.settings') + '#budgets')

@budgets_bp.route('/goals')
def goals():
    goals = SavingGoal.query.all()
    goal_stats = []
    
    for goal in goals:
        current_amount = float(goal.current_amount)
        
        if goal.category_id:
            category_savings = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.category_id == goal.category_id,
                Transaction.transaction_type.in_(['income', 'cash_in', 'bank_deposit']) 
            ).scalar() or 0
            current_amount += float(category_savings)
            
        percentage = (current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        remaining = goal.target_amount - current_amount
        
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

@budgets_bp.route('/goals/add', methods=['GET', 'POST'])
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
        return redirect(url_for('budgets.goals'))
    return render_template('add_goal.html', categories=Category.query.all())

@budgets_bp.route('/goals/<int:id>/update', methods=['POST'])
def update_goal(id):
    return redirect(url_for('budgets.goals'))

@budgets_bp.route('/goals/<int:id>/delete', methods=['POST'])
def delete_goal(id):
    goal = SavingGoal.query.get_or_404(id)
    db.session.delete(goal)
    db.session.commit()
    flash('Hedef silindi!', 'success')
    return redirect(url_for('budgets.goals'))
