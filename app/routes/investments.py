from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Investment, Account, Transaction

investments_bp = Blueprint('investments', __name__, url_prefix='/investments')

@investments_bp.route('/')
@login_required
def index():
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    # Calculate portfolio values
    total_invested = sum(inv.amount for inv in investments)
    
    # Group by type for visual representation
    types_data = {}
    for inv in investments:
        types_data[inv.type] = types_data.get(inv.type, 0.0) + inv.amount
        
    return render_template(
        'investments.html',
        investments=investments,
        accounts=accounts,
        total_invested=total_invested,
        types_labels=list(types_data.keys()),
        types_values=list(types_data.values())
    )

@investments_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    inv_type = request.form.get('type')  # Tesouro Direto, CDB, ETFs, Ações, Criptomoedas
    amount = float(request.form.get('amount', 0.0))
    account_id = request.form.get('account_id')
    date_str = request.form.get('purchase_date')
    purchase_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
    
    if not name or not inv_type or amount <= 0 or not account_id:
        flash('Todos os campos, incluindo a conta bancária de origem, são obrigatórios.', 'warning')
        return redirect(url_for('investments.index'))
        
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    
    if account.balance < amount:
        flash(f'Saldo insuficiente na conta {account.name} (Saldo: R${account.balance:.2f}) para realizar este investimento.', 'danger')
        return redirect(url_for('investments.index'))
        
    # Deduct from account
    account.balance -= amount
    
    # Register investment
    new_inv = Investment(
        user_id=current_user.id,
        name=name,
        type=inv_type,
        amount=amount,
        purchase_date=purchase_date
    )
    
    # Record transaction
    inv_tx = Transaction(
        user_id=current_user.id,
        account_id=account.id,
        type='expense',
        category='Investimento',
        amount=amount,
        description=f'Compra de Ativo: {name} ({inv_type})',
        date=purchase_date
    )
    
    db.session.add(new_inv)
    db.session.add(inv_tx)
    db.session.commit()
    
    flash(f'Investimento de R${amount:.2f} em "{name}" registrado e pago com {account.name}!', 'success')
    return redirect(url_for('investments.index'))

@investments_bp.route('/redeem/<int:id>', methods=['POST'])
@login_required
def redeem(id):
    inv = Investment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    account_id = request.form.get('account_id')
    amount = float(request.form.get('amount', 0.0))
    
    if not account_id or amount <= 0 or amount > inv.amount:
        flash('Insira uma conta e um valor válido de resgate (menor ou igual ao valor investido).', 'warning')
        return redirect(url_for('investments.index'))
        
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    
    # Add to account
    account.balance += amount
    
    # Record transaction
    red_tx = Transaction(
        user_id=current_user.id,
        account_id=account.id,
        type='income',
        category='Resgate de Investimento',
        amount=amount,
        description=f'Resgate Parcial/Total: {inv.name}',
        date=datetime.utcnow().date()
    )
    
    # Adjust investment amount
    inv.amount -= amount
    if inv.amount < 0.01:  # Fully redeemed
        db.session.delete(inv)
        flash(f'Todo o investimento em "{inv.name}" foi resgatado e depositado em {account.name}!', 'success')
    else:
        flash(f'Resgatado R${amount:.2f} de "{inv.name}" para a conta {account.name}. Restante: R${inv.amount:.2f}', 'success')
        
    db.session.add(red_tx)
    db.session.commit()
    return redirect(url_for('investments.index'))

@investments_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    inv = Investment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(inv)
    db.session.commit()
    flash('Investimento removido sem impacto no saldo bancário.', 'info')
    return redirect(url_for('investments.index'))
