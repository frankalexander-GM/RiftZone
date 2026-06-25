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
            joinedload(Publicacion.reposteado).joinedload(Publicacion.autor),
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

    def get_general(self, user_id=None):
        return (
            self._base_query(user_id)
            .filter(
                (Publicacion.juego.is_(None)) |
                (Publicacion.juego == '')
            )
            .order_by(Publicacion.promocionada.desc(), Publicacion.fecha_creacion.desc())
            .all()
        )

    def get_videos(self, user_id=None):
        from sqlalchemy import or_
        return (
            self._base_query(user_id)
            .filter(or_(
                Publicacion.video_archivo.isnot(None),
                Publicacion.contenido.like('[Clip]%')
            ))
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
    
    def get_for_you(self, user_id=None):
        import datetime
        from collections import defaultdict
        posts = self.get_all_descending(user_id)
        
        if not user_id:
            def guest_score(p):
                engagement = (p.likes_count or 0) * 10 + (p.comentarios_count or 0) * 15
                if p.promocionada:
                    engagement += 200
                if p.boost_tipo:
                    engagement += 100
                return engagement
            return sorted(posts, key=guest_score, reverse=True)
            
        from app.models.usuario import seguidores
        followed_users = set()
        if self.session:
            rows = self.session.execute(
                seguidores.select().where(seguidores.c.seguidor_id == user_id)
            ).all()
            followed_users = {row.seguido_id for row in rows}
        else:
            from app.factories.app_factory import db
            rows = db.session.execute(
                seguidores.select().where(seguidores.c.seguidor_id == user_id)
            ).all()
            followed_users = {row.seguido_id for row in rows}
            
        def user_score(p):
            score = 0
            score += (p.likes_count or 0) * 10
            score += (p.comentarios_count or 0) * 15
            if p.id_usuario in followed_users:
                score += 80
            if p.promocionada:
                score += 200
            if p.boost_tipo:
                score += 100
            if p.fecha_creacion:
                hours_ago = (datetime.datetime.utcnow() - p.fecha_creacion).total_seconds() / 3600.0
                score += max(0, 100 - hours_ago * 2)
            return score
        
        by_game = defaultdict(list)
        for p in posts:
            game = p.juego or '__general__'
            by_game[game].append(p)
        
        per_game_limit = 4
        selected = []
        for game, game_posts in by_game.items():
            game_posts.sort(key=user_score, reverse=True)
            selected.extend(game_posts[:per_game_limit])
        
        followed_posts = [p for p in posts if p.id_usuario in followed_users and p not in selected]
        followed_posts.sort(key=user_score, reverse=True)
        selected.extend(followed_posts[:10])
        
        selected.sort(key=user_score, reverse=True)
        
        games_order = []
        result = []
        remaining = {p.id_publicacion: p for p in selected}
        
        boosted = [p for p in selected if p.promocionada]
        for p in boosted:
            if p.id_publicacion in remaining:
                result.append(p)
                del remaining[p.id_publicacion]
        
        while remaining:
            games_used = {p.juego or '__general__' for p in result[-8:]}
            candidates = [p for pid, p in remaining.items() if (p.juego or '__general__') not in games_used]
            if not candidates:
                candidates = list(remaining.values())
            candidates.sort(key=lambda p: (p.juego or '__general__') not in games_used, reverse=True)
            next_p = candidates[0]
            result.append(next_p)
            del remaining[next_p.id_publicacion]
        
        return result
    
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
