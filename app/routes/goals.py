from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Goal, Account, Transaction

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

@goals_bp.route('/')
@login_required
def index():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    goals_list = []
    for goal in goals:
        percent = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        goals_list.append({
            'id': goal.id,
            'name': goal.name,
            'target_amount': goal.target_amount,
            'current_amount': goal.current_amount,
            'percent': min(percent, 100),
            'raw_percent': percent,
            'deadline': goal.deadline
        })
        
    return render_template('goals.html', goals=goals_list, accounts=accounts)

@goals_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    target_amount = float(request.form.get('target_amount', 0.0))
    deadline_str = request.form.get('deadline')
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
    
    if not name or target_amount <= 0:
        flash('Nome da meta e valor alvo são obrigatórios.', 'warning')
        return redirect(url_for('goals.index'))
        
    new_goal = Goal(
        user_id=current_user.id,
        name=name,
        target_amount=target_amount,
        current_amount=0.0,
        deadline=deadline
    )
    db.session.add(new_goal)
    db.session.commit()
    flash('Meta financeira cadastrada com sucesso!', 'success')
    return redirect(url_for('goals.index'))

@goals_bp.route('/deposit/<int:id>', methods=['POST'])
@login_required
def deposit(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    account_id = request.form.get('account_id')
    amount = float(request.form.get('amount', 0.0))
    
    if not account_id or amount <= 0:
        flash('Selecione uma conta bancária e insira um valor válido.', 'warning')
        return redirect(url_for('goals.index'))
        
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    
    if account.balance < amount:
        flash(f'Saldo insuficiente na conta {account.name} (Saldo: R${account.balance:.2f}).', 'danger')
        return redirect(url_for('goals.index'))
        
    # Deduct from account
    account.balance -= amount
    
    # Add to goal
    goal.current_amount += amount
    
    # Record transaction
    deposit_tx = Transaction(
        user_id=current_user.id,
        account_id=account.id,
        type='expense',
        category='Reserva/Meta',
        amount=amount,
        description=f'Depósito na Meta: {goal.name}',
        date=datetime.utcnow().date()
    )
    
    db.session.add(deposit_tx)
    db.session.commit()
    
    flash(f'R${amount:.2f} transferidos de {account.name} para a meta "{goal.name}"!', 'success')
    return redirect(url_for('goals.index'))

@goals_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Meta financeira excluída.', 'info')
    return redirect(url_for('goals.index'))
