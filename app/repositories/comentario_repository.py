from app.models.comentario import Comentario

class ComentarioRepository:
    """Repositorio de comentarios - GamesSphere"""
    
    def __init__(self, session=None):
        self.session = session
    
    def create(self, **kwargs):
        from app.factories.app_factory import db
        comentario = Comentario(**kwargs)
        db.session.add(comentario)
        db.session.commit()
        return comentario
