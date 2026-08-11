from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import BillPayable, BillReceivable, Account, Transaction

bills_bp = Blueprint('bills', __name__, url_prefix='/bills')

@bills_bp.route('/')
@login_required
def index():
    bills_payable = BillPayable.query.filter_by(user_id=current_user.id).order_by(BillPayable.due_date.asc()).all()
    bills_receivable = BillReceivable.query.filter_by(user_id=current_user.id).order_by(BillReceivable.expected_date.asc()).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('bills.html', bills_payable=bills_payable, bills_receivable=bills_receivable, accounts=accounts)

@bills_bp.route('/payable/add', methods=['POST'])
@login_required
def add_payable():
    name = request.form.get('name')
    amount = float(request.form.get('amount', 0.0))
    due_date_str = request.form.get('due_date')
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else datetime.utcnow().date()
    
    if not name:
        flash('O nome da conta a pagar é obrigatório.', 'warning')
        return redirect(url_for('bills.index'))
        
    new_bill = BillPayable(user_id=current_user.id, name=name, amount=amount, due_date=due_date, status='pending')
    db.session.add(new_bill)
    db.session.commit()
    flash('Conta a pagar registrada com sucesso!', 'success')
    return redirect(url_for('bills.index'))

@bills_bp.route('/receivable/add', methods=['POST'])
@login_required
def add_receivable():
    name = request.form.get('name')
    amount = float(request.form.get('amount', 0.0))
    expected_date_str = request.form.get('expected_date')
    expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d').date() if expected_date_str else datetime.utcnow().date()
    
    if not name:
        flash('O nome do valor a receber é obrigatório.', 'warning')
        return redirect(url_for('bills.index'))
        
    new_bill = BillReceivable(user_id=current_user.id, name=name, amount=amount, expected_date=expected_date, status='pending')
    db.session.add(new_bill)
    db.session.commit()
    flash('Conta a receber registrada com sucesso!', 'success')
    return redirect(url_for('bills.index'))

@bills_bp.route('/payable/pay/<int:id>', methods=['POST'])
@login_required
def pay_payable(id):
    bill = BillPayable.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    account_id = request.form.get('account_id')
    
    if not account_id:
        flash('Selecione uma conta bancária para efetuar o pagamento.', 'warning')
        return redirect(url_for('bills.index'))
        
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    
    # Update status
    bill.status = 'paid'
    
    # Deduct from bank account
    account.balance -= bill.amount
    
    # Record transaction
    pay_tx = Transaction(
        user_id=current_user.id,
        account_id=account.id,
        type='expense',
        category='Pagamento de Conta',
        amount=bill.amount,
        description=f'Pagamento de Conta - {bill.name}',
        date=datetime.utcnow().date()
    )
    
    db.session.add(pay_tx)
    db.session.commit()
    flash(f'Conta "{bill.name}" marcada como paga e debitada de {account.name}!', 'success')
    return redirect(url_for('bills.index'))

@bills_bp.route('/receivable/receive/<int:id>', methods=['POST'])
@login_required
def receive_receivable(id):
    bill = BillReceivable.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    account_id = request.form.get('account_id')
    
    if not account_id:
        flash('Selecione uma conta bancária para depositar o valor.', 'warning')
        return redirect(url_for('bills.index'))
        
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    
    # Update status
    bill.status = 'received'
    
    # Add to bank account
    account.balance += bill.amount
    
    # Record transaction
    rec_tx = Transaction(
        user_id=current_user.id,
        account_id=account.id,
        type='income',
        category='Recebimento de Conta',
        amount=bill.amount,
        description=f'Recebimento - {bill.name}',
        date=datetime.utcnow().date()
    )
    
    db.session.add(rec_tx)
    db.session.commit()
    flash(f'Valor "{bill.name}" marcado como recebido e depositado em {account.name}!', 'success')
    return redirect(url_for('bills.index'))

@bills_bp.route('/payable/delete/<int:id>', methods=['POST'])
@login_required
def delete_payable(id):
    bill = BillPayable.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(bill)
    db.session.commit()
    flash('Conta a pagar excluída.', 'info')
    return redirect(url_for('bills.index'))

@bills_bp.route('/receivable/delete/<int:id>', methods=['POST'])
@login_required
def delete_receivable(id):
    bill = BillReceivable.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(bill)
    db.session.commit()
    flash('Conta a receber excluída.', 'info')
    return redirect(url_for('bills.index'))
