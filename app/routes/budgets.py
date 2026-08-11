from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import func
from app import db
from app.models import Budget, Transaction

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@budgets_bp.route('/')
@login_required
def index():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    
    # Calculate current spent dynamically for each budget's category in the current month
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    
    budgets_list = []
    for budget in budgets:
        # Sum of expense transactions for this category in the current month
        spent = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            Transaction.category == budget.category,
            Transaction.date >= first_day_of_month
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0.0
        
        # We can update the budget db field or just use it dynamically in view
        budget.current_spent = spent
        db.session.add(budget)
        
        percent = (spent / budget.amount_limit * 100) if budget.amount_limit > 0 else 0
        budgets_list.append({
            'id': budget.id,
            'category': budget.category,
            'amount_limit': budget.amount_limit,
            'current_spent': spent,
            'percent': min(percent, 100),
            'raw_percent': percent,
            'period': budget.period
        })
        
    db.session.commit()
    return render_template('budgets.html', budgets=budgets_list)

@budgets_bp.route('/add', methods=['POST'])
@login_required
def add():
    category = request.form.get('category')
    amount_limit = float(request.form.get('amount_limit', 0.0))
    period = request.form.get('period', 'monthly')
    
    if not category or amount_limit <= 0:
        flash('Categoria e limite de gastos válidos são obrigatórios.', 'warning')
        return redirect(url_for('budgets.index'))
        
    # Check if budget for this category already exists
    existing = Budget.query.filter_by(user_id=current_user.id, category=category).first()
    if existing:
        flash(f'Já existe um orçamento cadastrado para a categoria "{category}".', 'warning')
        return redirect(url_for('budgets.index'))
        
    new_budget = Budget(
        user_id=current_user.id,
        category=category,
        amount_limit=amount_limit,
        period=period
    )
    db.session.add(new_budget)
    db.session.commit()
    flash('Orçamento cadastrado com sucesso!', 'success')
    return redirect(url_for('budgets.index'))

@budgets_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    budget.amount_limit = float(request.form.get('amount_limit', 0.0))
    budget.period = request.form.get('period', 'monthly')
    db.session.commit()
    flash('Orçamento atualizado com sucesso!', 'success')
    return redirect(url_for('budgets.index'))

@budgets_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(budget)
    db.session.commit()
    flash('Orçamento excluído.', 'info')
    return redirect(url_for('budgets.index'))
