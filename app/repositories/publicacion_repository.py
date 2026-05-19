from app.models.publicacion import Publicacion

class PublicacionRepository:
    """Repositorio de publicaciones - GamesSphere"""
    
    def __init__(self, session=None):
        self.session = session
    
    def get_by_id(self, post_id):
        return Publicacion.query.get(post_id)
    
    def get_all_descending(self):
        return Publicacion.query.order_by(Publicacion.fecha_creacion.desc()).all()
    
    def create(self, **kwargs):
        from app.factories.app_factory import db
        post = Publicacion(**kwargs)
        db.session.add(post)
        db.session.commit()
        return post

    def toggle_like(self, post, usuario):
        from app.factories.app_factory import db
        if usuario in post.usuarios_likes:
            post.usuarios_likes.remove(usuario)
            liked = False
        else:
            post.usuarios_likes.append(usuario)
            liked = True
        db.session.commit()
        return liked
