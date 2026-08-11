from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, date, timedelta
from collections import defaultdict
from app.models import Transaction, Account, Investment

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    # 1. Income vs Expense last 6 months
    today = date.today()
    six_months_ago = today - timedelta(days=180)
    
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= six_months_ago
    ).all()
    
    # Group by month string 'YYYY-MM'
    monthly_data = defaultdict(lambda: {'income': 0.0, 'expense': 0.0})
    for tx in transactions:
        month_str = tx.date.strftime('%Y-%m')
        if tx.type == 'income':
            monthly_data[month_str]['income'] += tx.amount
        elif tx.type == 'expense':
            monthly_data[month_str]['expense'] += tx.amount
            
    # Sort months chronologically
    sorted_months = sorted(list(monthly_data.keys()))
    income_by_month = [monthly_data[m]['income'] for m in sorted_months]
    expense_by_month = [monthly_data[m]['expense'] for m in sorted_months]
    net_flow_by_month = [monthly_data[m]['income'] - monthly_data[m]['expense'] for m in sorted_months]
    
    # 2. Expenses by category in current month
    first_day_of_month = date(today.year, today.month, 1)
    current_month_expenses = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date >= first_day_of_month
    ).all()
    
    category_expenses = defaultdict(float)
    for tx in current_month_expenses:
        category_expenses[tx.category] += tx.amount
        
    category_labels = list(category_expenses.keys())
    category_values = list(category_expenses.values())
    
    # 3. Wealth composition (Evolução / Distribuição Patrimonial)
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    
    total_cash = sum(acc.balance for acc in accounts)
    total_invested = sum(inv.amount for inv in investments)
    
    wealth_composition_labels = ['Dinheiro em Conta', 'Investimentos']
    wealth_composition_values = [total_cash, total_invested]
    
    return render_template(
        'reports.html',
        months=sorted_months,
        income_by_month=income_by_month,
        expense_by_month=expense_by_month,
        net_flow_by_month=net_flow_by_month,
        category_labels=category_labels,
        category_values=category_values,
        wealth_labels=wealth_composition_labels,
        wealth_values=wealth_composition_values,
        total_assets=total_cash + total_invested
    )
