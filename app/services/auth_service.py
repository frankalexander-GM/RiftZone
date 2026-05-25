from app.factories.app_factory import bcrypt

class AuthService:
    """Servicio de autenticación - RiftZone"""
    
    def __init__(self, user_repo):
        self.user_repo = user_repo
    
    def login(self, email, password):
        user = self.user_repo.get_by_email(email)
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return None
    
    def register(self, nombre, username, email, password):
        # Validación de contraseña
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        
        # Validación de email
        if self.user_repo.get_by_email(email):
            raise ValueError("El correo electrónico ya está registrado.")
            
        # Validación de username (opcional pero buena práctica)
        if self.user_repo.get_by_username(username):
            raise ValueError("El nombre de usuario ya está en uso.")

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        return self.user_repo.create(
            nombre=nombre,
            username=username,
            email=email,
            password=hashed
        )
