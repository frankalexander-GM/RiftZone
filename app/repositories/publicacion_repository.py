from app.models.publicacion import Publicacion, publicacion_likes, publicacion_oculta

class PublicacionRepository:
    """Repositorio de publicaciones - GamesSphere"""
    
    def __init__(self, session=None):
        self.session = session
    
    def _base_query(self, user_id=None):
        from sqlalchemy.orm import joinedload
        from app.models.comentario import Comentario
        q = Publicacion.query.options(
            joinedload(Publicacion.autor),
            joinedload(Publicacion.usuarios_likes),
            joinedload(Publicacion.comentarios).joinedload(Comentario.autor),
        )
        if user_id is not None:
            q = q.outerjoin(publicacion_oculta,
                (Publicacion.id_publicacion == publicacion_oculta.c.id_publicacion) &
                (publicacion_oculta.c.id_usuario == user_id)
            ).filter(publicacion_oculta.c.id_usuario.is_(None))
        return q

    def get_by_id(self, post_id):
        return Publicacion.query.get(post_id)
    
    def get_all_descending(self, user_id=None):
        return (
            self._base_query(user_id)
            .order_by(Publicacion.promocionada.desc(), Publicacion.fecha_creacion.desc())
            .all()
        )
    
    def get_recent(self, user_id=None):
        return (
            self._base_query(user_id)
            .order_by(Publicacion.fecha_creacion.desc())
            .all()
        )
    
    def get_popular(self, user_id=None):
        from app.factories.app_factory import db
        from sqlalchemy import func as safunc
        like_count = (
            db.session.query(publicacion_likes.c.id_publicacion, safunc.count(publicacion_likes.c.id_usuario).label('cnt'))
            .group_by(publicacion_likes.c.id_publicacion)
            .subquery()
        )
        return (
            self._base_query(user_id)
            .outerjoin(like_count, Publicacion.id_publicacion == like_count.c.id_publicacion)
            .order_by(like_count.c.cnt.desc().nullslast(), Publicacion.fecha_creacion.desc())
            .all()
        )
    
    def get_encuestas(self, user_id=None):
        from app.models.publicacion import Poll
        return (
            self._base_query(user_id)
            .join(Poll, Publicacion.id_publicacion == Poll.id_publicacion)
            .order_by(Publicacion.fecha_creacion.desc())
            .all()
        )

    def get_torneos(self, user_id=None):
        return (
            self._base_query(user_id)
            .filter(Publicacion.contenido.like('[Torneo]%'))
            .order_by(Publicacion.fecha_creacion.desc())
            .all()
        )

    def get_following(self, user_id):
        from app.models.usuario import seguidores
        return (
            self._base_query(user_id)
            .join(Publicacion.autor)
            .join(seguidores, seguidores.c.seguido_id == Publicacion.id_usuario)
            .filter(seguidores.c.seguidor_id == user_id)
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
