from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Account

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@accounts_bp.route('/')
@login_required
def index():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('accounts.html', accounts=accounts)

@accounts_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    acc_type = request.form.get('type')
    balance = float(request.form.get('balance', 0.0))
    
    if not name or not acc_type:
        flash('Nome e tipo de conta são obrigatórios.', 'warning')
        return redirect(url_for('accounts.index'))
        
    new_account = Account(user_id=current_user.id, name=name, type=acc_type, balance=balance)
    db.session.add(new_account)
    db.session.commit()
    
    flash('Conta bancária cadastrada com sucesso!', 'success')
    return redirect(url_for('accounts.index'))

@accounts_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    account = Account.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    account.name = request.form.get('name')
    account.type = request.form.get('type')
    account.balance = float(request.form.get('balance', 0.0))
    
    db.session.commit()
    flash('Conta bancária atualizada com sucesso!', 'success')
    return redirect(url_for('accounts.index'))

@accounts_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    account = Account.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(account)
    db.session.commit()
    flash('Conta bancária excluída.', 'info')
    return redirect(url_for('accounts.index'))
