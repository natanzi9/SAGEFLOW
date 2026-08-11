from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Transaction, Account, Card, Budget, Goal, Investment, BillPayable, BillReceivable
from app.seed import seed_database

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'profile':
            username = request.form.get('username')
            email = request.form.get('email')
            
            # Check if username/email already taken by another user
            existing = User.query.filter((User.username == username) | (User.email == email)).filter(User.id != current_user.id).first()
            if existing:
                flash('Nome de usuário ou email já estão sendo utilizados por outra conta.', 'danger')
                return redirect(url_for('settings.index'))
                
            current_user.username = username
            current_user.email = email
            db.session.commit()
            flash('Informações do perfil atualizadas!', 'success')
            
        elif action == 'password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            
            if not current_user.check_password(current_password):
                flash('Senha atual incorreta.', 'danger')
                return redirect(url_for('settings.index'))
                
            current_user.set_password(new_password)
            db.session.commit()
            flash('Senha atualizada com sucesso!', 'success')
            
        return redirect(url_for('settings.index'))
        
    return render_template('settings.html')

@settings_bp.route('/reset-db', methods=['POST'])
@login_required
def reset_db():
    try:
        # Delete user's financial entities
        Transaction.query.filter_by(user_id=current_user.id).delete()
        Account.query.filter_by(user_id=current_user.id).delete()
        Card.query.filter_by(user_id=current_user.id).delete()
        Budget.query.filter_by(user_id=current_user.id).delete()
        Goal.query.filter_by(user_id=current_user.id).delete()
        Investment.query.filter_by(user_id=current_user.id).delete()
        BillPayable.query.filter_by(user_id=current_user.id).delete()
        BillReceivable.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        flash('Todas as suas informações financeiras foram limpas com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao limpar dados: {e}', 'danger')
        
    return redirect(url_for('settings.index'))

@settings_bp.route('/reseed-db', methods=['POST'])
@login_required
def reseed_db():
    try:
        # Clear existing financial details first
        Transaction.query.filter_by(user_id=current_user.id).delete()
        Account.query.filter_by(user_id=current_user.id).delete()
        Card.query.filter_by(user_id=current_user.id).delete()
        Budget.query.filter_by(user_id=current_user.id).delete()
        Goal.query.filter_by(user_id=current_user.id).delete()
        Investment.query.filter_by(user_id=current_user.id).delete()
        BillPayable.query.filter_by(user_id=current_user.id).delete()
        BillReceivable.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        # We delete user so seed_database creates it clean, or we can seed manually
        # But to make it simple, we delete the demo user and let seed_database regenerate it
        # If the logged in user is the demo user, delete the user and log them out
        is_demo = current_user.username == 'demo'
        
        if is_demo:
            db.session.delete(current_user)
            db.session.commit()
            seed_database()
            flash('Banco de dados de demonstração recarregado! Por favor, faça login novamente.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Carga de simulação só é permitida na conta demonstrativa.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao repopular dados: {e}', 'danger')
        
    return redirect(url_for('settings.index'))
