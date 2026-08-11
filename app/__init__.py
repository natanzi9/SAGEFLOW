import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sageflow-super-secret-key-1234')
    
    # Use SQLite by default for simplicity, but easily switchable to MySQL via ENV
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///sageflow.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize Extensions
    db.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transactions_bp
    from app.routes.accounts import accounts_bp
    from app.routes.cards import cards_bp
    from app.routes.bills import bills_bp
    from app.routes.budgets import budgets_bp
    from app.routes.goals import goals_bp
    from app.routes.investments import investments_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp
    from app.routes.tutorial import tutorial_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(investments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(tutorial_bp)
    
    # User loader callback
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()
        try:
            from app.seed import seed_database
            seed_database()
        except Exception as e:
            app.logger.error(f"Erro ao rodar seed: {e}")
        
    return app
