from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Category, Tag, Transaction

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories')
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

@categories_bp.route('/categories/add', methods=['GET', 'POST'])
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
        return redirect(url_for('main.settings') + '#categories')
    return render_template('add_category.html')

@categories_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        category.icon = request.form.get('icon')
        category.color = request.form.get('color', '#6c757d')
        db.session.commit()
        flash('Kategori güncellendi!', 'success')
        return redirect(url_for('categories.categories'))
    return render_template('edit_category.html', category=category)

@categories_bp.route('/categories/<int:id>/delete', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Kategori silindi!', 'success')
    return redirect(url_for('main.settings') + '#categories')

@categories_bp.route('/tags')
def tags():
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)

@categories_bp.route('/tags/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        tag = Tag(
            name=request.form['name'],
            color=request.form.get('color', '#17a2b8')
        )
        db.session.add(tag)
        db.session.commit()
        flash('Etiket eklendi!', 'success')
        return redirect(url_for('main.settings') + '#tags')
    return render_template('add_tag.html')

@categories_bp.route('/tags/<int:id>/delete', methods=['POST'])
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('Etiket silindi!', 'success')
    return redirect(url_for('main.settings') + '#tags')
