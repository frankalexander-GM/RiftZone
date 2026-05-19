class UsuarioService:
    """Servicio de usuarios - GamesSphere"""
    
    def __init__(self, user_repo):
        self.user_repo = user_repo
    
    def get_perfil(self, user_id):
        return self.user_repo.get_by_id(user_id)
    
    def get_by_username(self, username):
        return self.user_repo.get_by_username(username)
    
    def actualizar_perfil(self, user_id, **kwargs):
        user = self.user_repo.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            from app.factories.app_factory import db
            db.session.commit()
        return user

    def search_users(self, query):
        if not query or not query.strip():
            return []
        return self.user_repo.search(query.strip())
