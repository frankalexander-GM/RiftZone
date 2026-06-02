class RepositoryFactory:
    """Fábrica para crear repositorios de datos"""
    @staticmethod
    def create_user_repository(session=None):
        from app.repositories.usuario_repository import UsuarioRepository
        return UsuarioRepository(session)

    @staticmethod
    def create_publicacion_repository(session=None):
        from app.repositories.publicacion_repository import PublicacionRepository
        return PublicacionRepository(session)

    @staticmethod
    def create_comentario_repository(session=None):
        from app.repositories.comentario_repository import ComentarioRepository
        return ComentarioRepository(session)
