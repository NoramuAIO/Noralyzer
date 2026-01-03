from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    app.config['SECRET_KEY'] = 'noralyzer-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/noralyzer.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.transactions import transactions_bp
    from app.routes.banks import banks_bp
    from app.routes.cards import cards_bp
    from app.routes.persons import persons_bp
    from app.routes.places import places_bp
    from app.routes.categories import categories_bp
    from app.routes.budgets import budgets_bp
    from app.routes.reports import reports_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(banks_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(persons_bp)
    app.register_blueprint(places_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(reports_bp)
    
    return app
