class ComentarioService:
    """Servicio de comentarios - GamesSphere"""
    
    def __init__(self, com_repo):
        self.com_repo = com_repo
        
    def crear_comentario(self, id_publicacion, id_usuario, contenido):
        if not contenido or not contenido.strip():
            raise ValueError("El comentario no puede estar vacío.")
            
        return self.com_repo.create(
            id_publicacion=id_publicacion,
            id_usuario=id_usuario,
            contenido=contenido
        )
