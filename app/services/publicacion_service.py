class PublicacionService:
    """Servicio de publicaciones - GamesSphere"""
    
    def __init__(self, pub_repo):
        self.pub_repo = pub_repo
        
    def crear_publicacion(self, id_usuario, contenido, juego, imagen_url=None):
        if not contenido or not contenido.strip():
            raise ValueError("El contenido de la publicación no puede estar vacío.")
        if not juego:
            raise ValueError("Debes asociar la publicación a un juego.")
            
        return self.pub_repo.create(
            id_usuario=id_usuario,
            contenido=contenido,
            juego=juego,
            imagen_url=imagen_url
        )
        
    def obtener_feed(self, tab='para-ti', user_id=None):
        from app.services.boost_service import limpiar_boosts_expirados
        limpiar_boosts_expirados()

        if tab == 'siguiendo' and user_id:
            return self.pub_repo.get_following(user_id)
        elif tab == 'populares':
            return self.pub_repo.get_popular(user_id)
        elif tab == 'recientes':
            return self.pub_repo.get_recent(user_id)
        elif tab == 'encuestas':
            return self.pub_repo.get_encuestas(user_id)
        elif tab == 'torneos':
            return self.pub_repo.get_torneos(user_id)
        else:
            return self.pub_repo.get_all_descending(user_id)

    def toggle_like(self, id_publicacion, usuario):
        post = self.pub_repo.get_by_id(id_publicacion)
        if not post:
            raise ValueError("Publicación no encontrada.")
        return self.pub_repo.toggle_like(post, usuario)

    def promocionar_publicacion(self, id_publicacion, id_usuario):
        post = self.pub_repo.get_by_id(id_publicacion)
        if not post:
            raise ValueError("Publicación no encontrada.")
        if post.id_usuario != id_usuario:
            raise ValueError("No tienes permiso para promocionar esta publicación.")
        return self.pub_repo.promocionar(post)
