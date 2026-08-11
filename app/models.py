from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Relationships
    accounts = db.relationship('Account', backref='user', lazy=True, cascade="all, delete-orphan")
    cards = db.relationship('Card', backref='user', lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade="all, delete-orphan")
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade="all, delete-orphan")
    goals = db.relationship('Goal', backref='user', lazy=True, cascade="all, delete-orphan")
    investments = db.relationship('Investment', backref='user', lazy=True, cascade="all, delete-orphan")
    bills_payable = db.relationship('BillPayable', backref='user', lazy=True, cascade="all, delete-orphan")
    bills_receivable = db.relationship('BillReceivable', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Conta Corrente, Poupança, Carteira Digital
    balance = db.Column(db.Float, default=0.0, nullable=False)
    currency = db.Column(db.String(10), default='BRL', nullable=False)

    # Relationships
    transactions = db.relationship('Transaction', foreign_keys='Transaction.account_id', backref='account', lazy=True)
    transfers_to = db.relationship('Transaction', foreign_keys='Transaction.destination_account_id', backref='destination_account', lazy=True)


class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Ex: Nubank Mastercard
    limit = db.Column(db.Float, nullable=False)
    due_day = db.Column(db.Integer, nullable=False)  # Dia de vencimento
    closing_day = db.Column(db.Integer, nullable=False)  # Dia de fechamento
    current_spend = db.Column(db.Float, default=0.0, nullable=False)

    transactions = db.relationship('Transaction', backref='card', lazy=True)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # income (receita), expense (despesa), transfer (transferência)
    category = db.Column(db.String(100), nullable=False)  # Alimentação, Salário, etc.
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    destination_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)  # For transfers


class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount_limit = db.Column(db.Float, nullable=False)
    current_spent = db.Column(db.Float, default=0.0, nullable=False)
    period = db.Column(db.String(20), default='monthly', nullable=False)


class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Viagem, Reserva de Emergência
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    deadline = db.Column(db.Date, nullable=True)


class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Tesouro Direto, CDB, ETFs, Ações, Criptomoedas
    amount = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)


class BillPayable(db.Model):
    __tablename__ = 'bills_payable'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Água, Luz, Internet, Aluguel
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, paid


class BillReceivable(db.Model):
    __tablename__ = 'bills_receivable'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Salário, Freelance, Comissão
    amount = db.Column(db.Float, nullable=False)
    expected_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, received
