from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Usuário ou email já cadastrado.', 'danger')
            return redirect(url_for('auth.register'))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça o login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Bem-vindo de volta, {user.username}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/recover-password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash('Senha redefinida com sucesso! Faça login com a nova senha.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email não encontrado no sistema.', 'danger')
            
    return render_template('auth/recover.html')
