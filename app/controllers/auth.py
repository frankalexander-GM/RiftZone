from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.factories.service_factory import get_service_factory

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('jugador.dashboard'))
    if request.method == 'POST':
        sf = get_service_factory()
        auth_service = sf.get_auth_service()
        
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Por favor ingresa tu correo y contraseña.', 'error')
            return render_template('auth/login.html')
            
        user = auth_service.login(email, password)
        if user:
            login_user(user)
            return redirect(url_for('jugador.dashboard'))
        flash('Credenciales inválidas. Verifica tu email y contraseña.', 'error')
    return render_template('auth/login.html')

import random

import uuid

@auth_bp.route('/login_guest')
def login_guest():
    sf = get_service_factory()
    auth_service = sf.get_auth_service()
    
    for _ in range(5):
        try:
            num = random.randint(10000, 99999)
            uid = str(uuid.uuid4())[:6]
            user = auth_service.register(
                nombre='Usuario Invitado',
                username=f'Invitado_{num}',
                email=f'invitado_{uid}@riftzone.tmp',
                password=f'Invitado{num}_{uid}'
            )
            
            user.rol = 'invitado'
            from app.factories.app_factory import db
            db.session.commit()
            
            login_user(user)
            flash('Has entrado en modo Invitado Temporal. Eres libre de explorar.', 'success')
            return redirect(url_for('jugador.dashboard'))
        except (ValueError, Exception):
            continue
    
    flash('Error al acceder como invitado. Intenta de nuevo.', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('jugador.dashboard'))
    if request.method == 'POST':
        sf = get_service_factory()
        auth_service = sf.get_auth_service()
        try:
            user = auth_service.register(
                nombre=request.form.get('nombre', ''),
                username=request.form.get('username', ''),
                email=request.form.get('email', ''),
                password=request.form.get('password', '')
            )
            login_user(user)
            flash('¡Registro exitoso! Bienvenido a tu nuevo perfil.', 'success')
            return redirect(url_for('jugador.perfil'))
        except Exception as e:
            flash(str(e), 'error')
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.home'))
