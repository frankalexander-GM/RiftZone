import re

from app.factories.app_factory import bcrypt
from app.utils.banner import DEFAULT_PROFILE_BANNER


class AuthService:
    """Servicio de autenticación - GamesSphere"""

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def login(self, email, password):
        user = self.user_repo.get_by_email(email.strip().lower())
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return None

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
