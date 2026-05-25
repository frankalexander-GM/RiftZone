class PublicacionService:
    """Servicio de publicaciones - RiftZone"""
    
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
        
    def obtener_feed(self):
        return self.pub_repo.get_all_descending()

    def toggle_like(self, id_publicacion, usuario):
        post = self.pub_repo.get_by_id(id_publicacion)
        if not post:
            raise ValueError("Publicación no encontrada.")
        return self.pub_repo.toggle_like(post, usuario)
