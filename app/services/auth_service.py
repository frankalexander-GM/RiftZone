import re
import random
import string
from datetime import datetime, timedelta, timezone

from app.factories.app_factory import bcrypt, db
from app.utils.banner import DEFAULT_PROFILE_BANNER


class AuthService:
    """Servicio de autenticación - RiftZone"""

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def login(self, identifier, password):
        """
        Intenta loguear al usuario con username o email.
        Retorna: (usuario, codigo_estado)
            codigo_estado:
                'ok'          — login exitoso
                'no_existe'   — el usuario/correo no está registrado
                'wrong_pass'  — contraseña incorrecta
                'invitado'    — cuenta de invitado temporal
        """
        identifier = identifier.strip()
        identifier_lower = identifier.lower()

        # Intentar buscar por username primero, luego por email
        user = self.user_repo.get_by_username(identifier_lower)
        if not user:
            user = self.user_repo.get_by_email(identifier_lower)

        if not user:
            return None, 'no_existe'

        if user.is_invitado():
            return None, 'invitado'

        if not bcrypt.check_password_hash(user.password, password):
            return user, 'wrong_pass'

        return user, 'ok'

    def register(self, nombre, username, email, password):
        nombre = nombre.strip()
        username = username.strip().lower()
        email = email.strip().lower()

        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        if len(nombre) > 50:
            raise ValueError("El nombre no puede superar los 50 caracteres.")

        if not username:
            raise ValueError("El nombre de usuario es obligatorio.")
        if len(username) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")
        if len(username) > 30:
            raise ValueError("El nombre de usuario no puede superar los 30 caracteres.")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("El nombre de usuario solo puede contener letras, números y guion bajo.")

        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            raise ValueError("El formato del correo electrónico no es válido.")

        if not password:
            raise ValueError("La contraseña es obligatoria.")
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not any(c.isupper() for c in password):
            raise ValueError("La contraseña debe contener al menos una mayúscula.")
        if not any(c.isdigit() for c in password):
            raise ValueError("La contraseña debe contener al menos un número.")

        if self.user_repo.get_by_email(email):
            raise ValueError("El correo electrónico ya está registrado.")

        if self.user_repo.get_by_username(username):
            raise ValueError("El nombre de usuario ya está en uso.")

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        return self.user_repo.create(
            nombre=nombre,
            username=username,
            email=email,
            password=hashed,
            banner=DEFAULT_PROFILE_BANNER,
        )

    # ─── Recuperación de contraseña por código ───

    @staticmethod
    def _generar_codigo(longitud=6):
        """Genera un código numérico aleatorio."""
        return ''.join(random.choices(string.digits, k=longitud))

    def solicitar_reset(self, email):
        """
        Genera un código de verificación y lo guarda en la BD.
        Retorna: (exito, mensaje, codigo_debug)
            codigo_debug solo se muestra en desarrollo (sin SMTP).
        """
        email = email.strip().lower()
        user = self.user_repo.get_by_email(email)

        if not user:
            return False, 'No encontramos una cuenta registrada con ese correo.', None

        if user.is_invitado():
            return False, 'Las cuentas de invitado no pueden restablecer su contraseña.', None

        # Invalidar códigos anteriores del usuario
        from app.models.usuario import PasswordResetCode
        PasswordResetCode.query.filter_by(
            usuario_id=user.id_usuario, usado=False
        ).update({'usado': True})

        # Generar nuevo código
        codigo = self._generar_codigo(6)
        expira = datetime.now(timezone.utc) + timedelta(minutes=15)

        reset_code = PasswordResetCode(
            usuario_id=user.id_usuario,
            codigo=codigo,
            expira_en=expira
        )
        db.session.add(reset_code)
        db.session.commit()

        # Intentar enviar por email (si está configurado)
        email_enviado = self._enviar_codigo_email(user.email, user.nombre, codigo)

        if email_enviado:
            return True, f'Se envió un código de verificación a {user.email}. Revisa tu bandeja de entrada (y spam).', None
        else:
            # Modo desarrollo: mostrar el código
            return True, f'Código de verificación (modo desarrollo): {codigo}', codigo

    @staticmethod
    def _enviar_codigo_email(destinatario, nombre, codigo):
        """
        Envía el código por correo. Retorna True si se envió, False si no.
        En desarrollo retorna False para mostrar el código en pantalla.
        """
        try:
            from flask import current_app
            mail = current_app.extensions.get('mail')
            if not mail:
                return False

            from flask_mail import Message
            msg = Message(
                subject='RiftZone — Código de verificación',
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@riftzone.com'),
                recipients=[destinatario]
            )
            msg.html = f'''
            <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; background: #0d0b1a; color: #e8e8ff; padding: 40px; border-radius: 16px; border: 1px solid rgba(167,139,250,0.2);">
                <h1 style="color: #A78BFA; text-align: center;">RiftZone</h1>
                <p style="color: #9d9db5;">Hola <strong style="color:#e8e8ff;">{nombre}</strong>,</p>
                <p style="color: #9d9db5;">Solicitaste restablecer tu contraseña. Tu código de verificación es:</p>
                <div style="background: rgba(124,58,237,0.15); border: 1px solid rgba(167,139,250,0.3); border-radius: 12px; padding: 20px; text-align: center; margin: 24px 0;">
                    <span style="font-size: 32px; font-weight: 900; letter-spacing: 8px; color: #C4B5FD;">{codigo}</span>
                </div>
                <p style="color: #9d9db5; font-size: 14px;">Este código expira en <strong style="color:#e8e8ff;">15 minutos</strong>. Si no lo solicitaste, ignora este mensaje.</p>
                <hr style="border: none; border-top: 1px solid rgba(167,139,250,0.1); margin: 24px 0;">
                <p style="color: #6b6b8d; font-size: 12px; text-align: center;">RiftZone — Tu zona gamer</p>
            </div>
            '''
            mail.send(msg)
            return True
        except Exception:
            return False

    def verificar_codigo(self, email, codigo):
        """
        Verifica si el código es válido para ese email.
        Retorna: (valido, mensaje)
        """
        email = email.strip().lower()
        user = self.user_repo.get_by_email(email)

        if not user:
            return False, 'No encontramos una cuenta con ese correo.'

        from app.models.usuario import PasswordResetCode
        ahora = datetime.now(timezone.utc)
        reset = PasswordResetCode.query.filter_by(
            usuario_id=user.id_usuario,
            codigo=codigo,
            usado=False
        ).filter(PasswordResetCode.expira_en > ahora).first()

        if not reset:
            return False, 'El código es inválido, ha expirado o ya fue usado.'

        return True, 'Código verificado correctamente.'

    def restablecer_password(self, email, codigo, nueva_password):
        """
        Verifica el código y cambia la contraseña.
        Retorna: (exito, mensaje)
        """
        email = email.strip().lower()
        user = self.user_repo.get_by_email(email)

        if not user:
            return False, 'No encontramos una cuenta con ese correo.'

        # Validar nueva contraseña
        if not nueva_password:
            return False, 'La contraseña es obligatoria.'
        if len(nueva_password) < 6:
            return False, 'La contraseña debe tener al menos 6 caracteres.'
        if not any(c.isupper() for c in nueva_password):
            return False, 'La contraseña debe contener al menos una mayúscula.'
        if not any(c.isdigit() for c in nueva_password):
            return False, 'La contraseña debe contener al menos un número.'

        # Verificar código
        from app.models.usuario import PasswordResetCode
        ahora = datetime.now(timezone.utc)
        reset = PasswordResetCode.query.filter_by(
            usuario_id=user.id_usuario,
            codigo=codigo,
            usado=False
        ).filter(PasswordResetCode.expira_en > ahora).first()

        if not reset:
            return False, 'El código es inválido, ha expirado o ya fue usado. Solicita uno nuevo.'

        # Cambiar contraseña
        hashed = bcrypt.generate_password_hash(nueva_password).decode('utf-8')
        user.password = hashed
        reset.usado = True
        db.session.commit()

        return True, 'Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.'