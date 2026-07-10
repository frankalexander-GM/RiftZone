from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.factories.service_factory import get_service_factory

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

# ─── LOGIN ───

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

        user, status = auth_service.login(email, password)

        if status == 'ok':
            login_user(user)
            flash(f'¡Bienvenido de vuelta, {user.nombre}!', 'success')
            return redirect(url_for('jugador.dashboard'))
        elif status == 'no_existe':
            flash('No encontramos una cuenta con ese correo. ¿Quizás necesitas <a href="{}" style="color:#A78BFA;text-decoration:underline;">registrarte</a>?'.format(url_for('auth.register')), 'error')
        elif status == 'wrong_pass':
            flash('La contraseña es incorrecta. <a href="{}" style="color:#A78BFA;text-decoration:underline;">¿Olvidaste tu contraseña?</a>'.format(url_for('auth.forgot_password')), 'error')
        elif status == 'invitado':
            flash('Las cuentas de invitado no pueden iniciar sesión de esta forma.', 'error')

        return render_template('auth/login.html')

    return render_template('auth/login.html')


# ─── LOGIN COMO INVITADO ───

import random
import uuid

@auth_bp.route('/login_guest')
def login_guest():
    if current_user.is_authenticated:
        return redirect(url_for('jugador.dashboard'))

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
            flash('Has entrado en modo Invitado. Eres libre de explorar.', 'success')
            return redirect(url_for('jugador.dashboard'))
        except ValueError:
            continue

    flash('Error al acceder como invitado. Intenta de nuevo.', 'error')
    return redirect(url_for('auth.login'))


# ─── REGISTRO ───

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
            flash('¡Registro exitoso! Bienvenido a RiftZone.', 'success')
            return redirect(url_for('jugador.perfil'))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('auth/register.html')


# ─── CERRAR SESIÓN ───

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.home'))


# ─── RECUPERAR CONTRASEÑA ───

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('jugador.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Ingresa tu correo electrónico.', 'error')
            return render_template('auth/forgot_password.html')

        sf = get_service_factory()
        auth_service = sf.get_auth_service()
        exito, mensaje, codigo_debug = auth_service.solicitar_reset(email)

        if exito:
            # Guardar email en sesión para el siguiente paso
            session['reset_email'] = email
            flash(mensaje, 'success')
            return redirect(url_for('auth.verify_code'))
        else:
            flash(mensaje, 'error')

    return render_template('auth/forgot_password.html')


@auth_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if current_user.is_authenticated:
        return redirect(url_for('jugador.dashboard'))

    email = session.get('reset_email')
    if not email:
        flash('Primero ingresa tu correo para solicitar el código.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        codigo = request.form.get('code', '').strip()
        if not codigo:
            flash('Ingresa el código de verificación.', 'error')
            return render_template('auth/verify_code.html', email=email)

        sf = get_service_factory()
        auth_service = sf.get_auth_service()
        valido, mensaje = auth_service.verificar_codigo(email, codigo)

        if valido:
            session['reset_verified'] = True
            flash('Código verificado. Ahora elige tu nueva contraseña.', 'success')
            return redirect(url_for('auth.reset_password'))
        else:
            flash(mensaje, 'error')

    return render_template('auth/verify_code.html', email=email)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('jugador.dashboard'))

    email = session.get('reset_email')
    verified = session.get('reset_verified')

    if not email or not verified:
        flash('Acceso no autorizado. Solicita un nuevo código.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not password or not confirm:
            flash('Completa ambos campos.', 'error')
            return render_template('auth/reset_password.html')

        if password != confirm:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('auth/reset_password.html')

        sf = get_service_factory()
        auth_service = sf.get_auth_service()

        # Necesitamos el código original para el servicio
        # Lo buscamos directamente
        from app.models.usuario import PasswordResetCode, Usuario
        from app.factories.app_factory import db
        from datetime import datetime, timezone

        user = Usuario.query.filter_by(email=email.strip().lower()).first()
        if not user:
            session.clear()
            flash('No encontramos esa cuenta.', 'error')
            return redirect(url_for('auth.forgot_password'))

        ahora = datetime.now(timezone.utc)
        reset = PasswordResetCode.query.filter_by(
            usuario_id=user.id_usuario,
            usado=False
        ).filter(PasswordResetCode.expira_en > ahora).order_by(PasswordResetCode.creado_en.desc()).first()

        if not reset:
            session.clear()
            flash('El código expiró. Solicita uno nuevo.', 'error')
            return redirect(url_for('auth.forgot_password'))

        exito, mensaje = auth_service.restablecer_password(email, reset.codigo, password)

        # Limpiar sesión
        session.pop('reset_email', None)
        session.pop('reset_verified', None)

        if exito:
            flash(mensaje, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(mensaje, 'error')

    return render_template('auth/reset_password.html')