from app.models.usuario import Usuario

class UsuarioRepository:
    """Repositorio de usuarios - GamesSphere"""
    
    def __init__(self, session=None):
        self.session = session
    
    def get_by_id(self, user_id):
        return Usuario.query.get(user_id)
    
    def get_by_username(self, username):
        return Usuario.query.filter_by(username=username).first()
    
    def get_by_email(self, email):
        return Usuario.query.filter_by(email=email).first()
    
    def get_all(self):
        return Usuario.query.all()
    
    def create(self, **kwargs):
        from app.factories.app_factory import db
        user = Usuario(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user

    def search(self, query):
        return Usuario.query.filter(Usuario.username.ilike(f'%{query}%') | Usuario.nombre.ilike(f'%{query}%')).all()
