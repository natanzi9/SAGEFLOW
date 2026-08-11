from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, date
from app.models import Account, Transaction, Goal, BillPayable, BillReceivable

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Calculate balance
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(account.balance for account in accounts)
    
    # Calculate Income/Expense for current month
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    
    # Total monthly income
    monthly_income = db_sum_transactions(current_user.id, 'income', first_day_of_month)
    # Total monthly expenses (from accounts)
    monthly_expenses = db_sum_transactions(current_user.id, 'expense', first_day_of_month)
    
    # Net savings
    savings = monthly_income - monthly_expenses
    
    # Goals
    goals = Goal.query.filter_by(user_id=current_user.id).limit(3).all()
    
    # Upcoming Bills Payable
    upcoming_payable = BillPayable.query.filter(
        BillPayable.user_id == current_user.id,
        BillPayable.status == 'pending',
        BillPayable.due_date >= today
    ).order_by(BillPayable.due_date.asc()).limit(3).all()
    
    # Upcoming Bills Receivable
    upcoming_receivable = BillReceivable.query.filter(
        BillReceivable.user_id == current_user.id,
        BillReceivable.status == 'pending',
        BillReceivable.expected_date >= today
    ).order_by(BillReceivable.expected_date.asc()).limit(3).all()
    
    # Chart Data: Income vs Expense Category breakdown
    categories_data = {}
    expenses_by_cat = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date >= first_day_of_month
    ).all()
    
    for tx in expenses_by_cat:
        categories_data[tx.category] = categories_data.get(tx.category, 0.0) + tx.amount

    return render_template(
        'dashboard.html',
        total_balance=total_balance,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        savings=savings,
        goals=goals,
        upcoming_payable=upcoming_payable,
        upcoming_receivable=upcoming_receivable,
        accounts=accounts,
        categories_labels=list(categories_data.keys()),
        categories_values=list(categories_data.values())
    )

def db_sum_transactions(user_id, tx_type, start_date):
    result = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.type == tx_type,
        Transaction.date >= start_date
    ).with_entities(func.sum(Transaction.amount)).scalar()
    return result if result is not None else 0.0
