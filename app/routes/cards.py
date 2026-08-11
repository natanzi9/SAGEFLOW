from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Card, Account, Transaction

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

@cards_bp.route('/')
@login_required
def index():
    cards = Card.query.filter_by(user_id=current_user.id).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('cards.html', cards=cards, accounts=accounts)

@cards_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    limit = float(request.form.get('limit', 0.0))
    due_day = int(request.form.get('due_day', 5))
    closing_day = int(request.form.get('closing_day', 28))
    
    if not name:
        flash('O nome do cartão é obrigatório.', 'warning')
        return redirect(url_for('cards.index'))
        
    new_card = Card(
        user_id=current_user.id,
        name=name,
        limit=limit,
        due_day=due_day,
        closing_day=closing_day,
        current_spend=0.0
    )
    db.session.add(new_card)
    db.session.commit()
    flash('Cartão de crédito registrado com sucesso!', 'success')
    return redirect(url_for('cards.index'))

@cards_bp.route('/pay_invoice/<int:id>', methods=['POST'])
@login_required
def pay_invoice(id):
    card = Card.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    account_id = request.form.get('account_id')
    
    if not account_id:
        flash('Selecione uma conta bancária para pagar a fatura.', 'warning')
        return redirect(url_for('cards.index'))
        
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    amount_to_pay = card.current_spend
    
    if amount_to_pay <= 0:
        flash('A fatura deste cartão está zerada.', 'info')
        return redirect(url_for('cards.index'))
        
    # Deduct from bank account
    account.balance -= amount_to_pay
    
    # Create transaction for record
    payment_tx = Transaction(
        user_id=current_user.id,
        account_id=account.id,
        type='expense',
        category='Pagamento de Fatura',
        amount=amount_to_pay,
        description=f'Pagamento de Fatura - {card.name}',
        date=datetime.utcnow().date()
    )
    
    # Reset card current spend
    card.current_spend = 0.0
    
    db.session.add(payment_tx)
    db.session.commit()
    
    flash(f'Fatura de R${amount_to_pay:.2f} paga com sucesso usando a conta {account.name}!', 'success')
    return redirect(url_for('cards.index'))

@cards_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    card = Card.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(card)
    db.session.commit()
    flash('Cartão excluído.', 'info')
    return redirect(url_for('cards.index'))
