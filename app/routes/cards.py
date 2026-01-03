from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Card, Bank, Transaction
from app.utils import get_currency_symbols

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/cards')
def cards():
    cards = Card.query.order_by(Card.is_favorite.desc(), Card.name).all()
    return render_template('cards.html', cards=cards)

@cards_bp.route('/cards/add', methods=['GET', 'POST'])
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
        return redirect(url_for('main.settings') + '#cards')
    return render_template('add_card.html', banks=Bank.query.all())

@cards_bp.route('/cards/<int:id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('cards.cards'))
    return render_template('edit_card.html', card=card, banks=Bank.query.all())

@cards_bp.route('/cards/<int:id>/toggle-favorite', methods=['POST'])
def toggle_card_favorite(id):
    card = Card.query.get_or_404(id)
    card.is_favorite = not card.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': card.is_favorite})

@cards_bp.route('/cards/<int:id>/delete', methods=['POST'])
def delete_card(id):
    card = Card.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    flash('Kart silindi!', 'success')
    return redirect(url_for('main.settings') + '#cards')

@cards_bp.route('/cards/<int:id>/transactions')
def card_transactions(id):
    card = Card.query.get_or_404(id)
    transactions = Transaction.query.filter_by(card_id=id).order_by(Transaction.date.desc()).all()
    total = sum(t.amount for t in transactions)
    return render_template('card_transactions.html', card=card, transactions=transactions, total=total, currency_symbols=get_currency_symbols())
