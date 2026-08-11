from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Transaction, Account, Card

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/')
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    cards = Card.query.filter_by(user_id=current_user.id).all()
    return render_template('transactions.html', transactions=transactions, accounts=accounts, cards=cards)

@transactions_bp.route('/add', methods=['POST'])
@login_required
def add():
    tx_type = request.form.get('type')  # income, expense, transfer
    category = request.form.get('category')
    amount = float(request.form.get('amount', 0.0))
    description = request.form.get('description')
    date_str = request.form.get('date')
    tx_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
    
    account_id = request.form.get('account_id')
    card_id = request.form.get('card_id')
    destination_account_id = request.form.get('destination_account_id')
    
    # Validation & Balance Updates
    if tx_type == 'income':
        if not account_id:
            flash('Selecione uma conta para a receita.', 'warning')
            return redirect(url_for('transactions.index'))
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
        account.balance += amount
        
        new_tx = Transaction(
            user_id=current_user.id,
            account_id=account.id,
            type=tx_type,
            category=category,
            amount=amount,
            description=description,
            date=tx_date
        )
        
    elif tx_type == 'expense':
        pay_method = request.form.get('pay_method')  # 'account' or 'card'
        if pay_method == 'account':
            if not account_id:
                flash('Selecione uma conta para a despesa.', 'warning')
                return redirect(url_for('transactions.index'))
            account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
            account.balance -= amount
            
            new_tx = Transaction(
                user_id=current_user.id,
                account_id=account.id,
                type=tx_type,
                category=category,
                amount=amount,
                description=description,
                date=tx_date
            )
        else:
            if not card_id:
                flash('Selecione um cartão para a despesa.', 'warning')
                return redirect(url_for('transactions.index'))
            card = Card.query.filter_by(id=card_id, user_id=current_user.id).first_or_404()
            card.current_spend += amount
            
            new_tx = Transaction(
                user_id=current_user.id,
                card_id=card.id,
                type=tx_type,
                category=category,
                amount=amount,
                description=description,
                date=tx_date
            )
            
    elif tx_type == 'transfer':
        if not account_id or not destination_account_id:
            flash('Selecione as contas de origem e destino.', 'warning')
            return redirect(url_for('transactions.index'))
        if account_id == destination_account_id:
            flash('As contas de origem e destino devem ser diferentes.', 'warning')
            return redirect(url_for('transactions.index'))
            
        src_acc = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
        dest_acc = Account.query.filter_by(id=destination_account_id, user_id=current_user.id).first_or_404()
        
        src_acc.balance -= amount
        dest_acc.balance += amount
        
        new_tx = Transaction(
            user_id=current_user.id,
            account_id=src_acc.id,
            destination_account_id=dest_acc.id,
            type=tx_type,
            category='Transferência',
            amount=amount,
            description=description,
            date=tx_date
        )
    else:
        flash('Tipo de transação inválido.', 'danger')
        return redirect(url_for('transactions.index'))
        
    db.session.add(new_tx)
    db.session.commit()
    flash('Transação registrada!', 'success')
    return redirect(url_for('transactions.index'))

@transactions_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    tx = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Revert balances
    if tx.type == 'income':
        if tx.account:
            tx.account.balance -= tx.amount
    elif tx.type == 'expense':
        if tx.account:
            tx.account.balance += tx.amount
        elif tx.card:
            tx.card.current_spend -= tx.amount
    elif tx.type == 'transfer':
        src_acc = Account.query.get(tx.account_id)
        dest_acc = Account.query.get(tx.destination_account_id)
        if src_acc:
            src_acc.balance += tx.amount
        if dest_acc:
            dest_acc.balance -= tx.amount
            
    db.session.delete(tx)
    db.session.commit()
    flash('Transação removida e saldos atualizados.', 'info')
    return redirect(url_for('transactions.index'))
