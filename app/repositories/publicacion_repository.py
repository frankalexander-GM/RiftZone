from app.models.publicacion import Publicacion

class PublicacionRepository:
    """Repositorio de publicaciones - GamesSphere"""
    
    def __init__(self, session=None):
        self.session = session
    
    def get_by_id(self, post_id):
        return Publicacion.query.get(post_id)
    
    def get_all_descending(self):
        from sqlalchemy.orm import joinedload
        from app.models.comentario import Comentario

        return (
            Publicacion.query.options(
                joinedload(Publicacion.autor),
                joinedload(Publicacion.usuarios_likes),
                joinedload(Publicacion.comentarios).joinedload(Comentario.autor),
            )
            .order_by(Publicacion.promocionada.desc(), Publicacion.fecha_creacion.desc())
            .all()
        )
    
    def promocionar(self, post):
        from app.factories.app_factory import db
        post.promocionada = True
        db.session.commit()
        return True
    
    def create(self, **kwargs):
        from app.factories.app_factory import db
        post = Publicacion(**kwargs)
        db.session.add(post)
        db.session.commit()
        return post

    def toggle_like(self, post, usuario):
        from app.factories.app_factory import db

        uid = usuario.id_usuario
        ya_like = next((u for u in post.usuarios_likes if u.id_usuario == uid), None)
        if ya_like:
            post.usuarios_likes.remove(ya_like)
            liked = False
        else:
            post.usuarios_likes.append(usuario)
            liked = True
        db.session.commit()
        db.session.refresh(post)
        return liked
