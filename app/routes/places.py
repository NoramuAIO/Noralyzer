from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Place, Transaction, Category
from app.utils import get_currency_symbols

places_bp = Blueprint('places', __name__)

@places_bp.route('/places')
def places():
    places = Place.query.order_by(Place.is_favorite.desc(), Place.name).all()
    return render_template('places.html', places=places)

@places_bp.route('/places/add', methods=['GET', 'POST'])
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
        return redirect(url_for('main.settings') + '#contacts')
    return render_template('add_place.html')

@places_bp.route('/places/<int:id>/edit', methods=['GET', 'POST'])
def edit_place(id):
    place = Place.query.get_or_404(id)
    if request.method == 'POST':
        place.name = request.form['name']
        place.address = request.form.get('address')
        place.category = request.form.get('category')
        place.is_favorite = bool(request.form.get('is_favorite'))
        db.session.commit()
        flash('Yer güncellendi!', 'success')
        return redirect(url_for('places.places'))
    return render_template('edit_place.html', place=place)

@places_bp.route('/places/<int:id>/toggle-favorite', methods=['POST'])
def toggle_place_favorite(id):
    place = Place.query.get_or_404(id)
    place.is_favorite = not place.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': place.is_favorite})

@places_bp.route('/places/<int:id>/delete', methods=['POST'])
def delete_place(id):
    place = Place.query.get_or_404(id)
    db.session.delete(place)
    db.session.commit()
    flash('Yer silindi!', 'success')
    return redirect(url_for('main.settings') + '#contacts')

@places_bp.route('/places/<int:id>/report')
def place_report(id):
    place = Place.query.get_or_404(id)
    transactions = Transaction.query.filter_by(place_id=id).order_by(Transaction.date.desc()).all()
    total_spent = sum(t.amount for t in transactions)
    
    category_breakdown = db.session.query(
        Category.name, db.func.sum(Transaction.amount)
    ).join(Transaction).filter(Transaction.place_id == id).group_by(Category.id).all()
    
    return render_template('place_report.html', place=place, transactions=transactions, 
                         total_spent=total_spent, category_breakdown=category_breakdown, currency_symbols=get_currency_symbols())
