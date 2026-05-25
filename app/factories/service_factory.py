"""Fábrica de servicios para RiftZone"""

class ServiceFactory:
    """Fábrica centralizada para crear servicios de negocio"""
    
    def __init__(self, session=None):
        self.session = session
        self._services = {}
    
    def get_auth_service(self):
        if 'auth' not in self._services:
            from app.services.auth_service import AuthService
            from app.factories.db_factory import RepositoryFactory
            user_repo = RepositoryFactory.create_user_repository(self.session)
            self._services['auth'] = AuthService(user_repo)
        return self._services['auth']
    
    def get_usuario_service(self):
        if 'usuario' not in self._services:
            from app.services.usuario_service import UsuarioService
            from app.factories.db_factory import RepositoryFactory
            user_repo = RepositoryFactory.create_user_repository(self.session)
            self._services['usuario'] = UsuarioService(user_repo)
        return self._services['usuario']

    def get_publicacion_service(self):
        if 'publicacion' not in self._services:
            from app.services.publicacion_service import PublicacionService
            from app.factories.db_factory import RepositoryFactory
            pub_repo = RepositoryFactory.create_publicacion_repository(self.session)
            self._services['publicacion'] = PublicacionService(pub_repo)
        return self._services['publicacion']

    def get_comentario_service(self):
        if 'comentario' not in self._services:
            from app.services.comentario_service import ComentarioService
            from app.factories.db_factory import RepositoryFactory
            com_repo = RepositoryFactory.create_comentario_repository(self.session)
            self._services['comentario'] = ComentarioService(com_repo)
        return self._services['comentario']

    def get_chat_service(self):
        if 'chat' not in self._services:
            from app.services.chat_service import ChatService
            self._services['chat'] = ChatService()
        return self._services['chat']
        
    def get_clan_service(self):
        if 'clan' not in self._services:
            from app.services.clan_service import ClanService
            self._services['clan'] = ClanService()
        return self._services['clan']

def get_service_factory(session=None):
    return ServiceFactory(session)
