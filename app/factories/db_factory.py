from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

class DatabaseFactory:
    """Fábrica para crear y gestionar conexiones a base de datos"""
    _engine = None
    _session_factory = None
    
    @classmethod
    def create_engine(cls, database_url=None, config_name='development'):
        if cls._engine is None:
            if database_url is None:
                from app.config.config import config
                database_url = config[config_name].SQLALCHEMY_DATABASE_URI
            engine_kwargs = {'pool_pre_ping': True, 'pool_recycle': 300}
            if 'sqlite' in database_url:
                engine_kwargs.update({
                    'poolclass': StaticPool,
                    'connect_args': {'check_same_thread': False}
                })
            cls._engine = create_engine(database_url, **engine_kwargs)
        return cls._engine
    
    @classmethod
    def create_session_factory(cls, engine=None):
        if cls._session_factory is None:
            if engine is None:
                engine = cls.create_engine()
            cls._session_factory = scoped_session(
                sessionmaker(bind=engine, autocommit=False, autoflush=False)
            )
        return cls._session_factory
    
    @classmethod
    def get_session(cls):
        if cls._session_factory is None:
            cls.create_session_factory()
        return cls._session_factory()
    
    @classmethod
    def close_session(cls):
        if cls._session_factory is not None:
            cls._session_factory.remove()

class RepositoryFactory:
    """Fábrica para crear repositorios de datos"""
    @staticmethod
    def create_user_repository(session=None):
        from app.repositories.usuario_repository import UsuarioRepository
        if session is None:
            session = DatabaseFactory.get_session()
        return UsuarioRepository(session)

    @staticmethod
    def create_publicacion_repository(session=None):
        from app.repositories.publicacion_repository import PublicacionRepository
        if session is None:
            session = DatabaseFactory.get_session()
        return PublicacionRepository(session)

    @staticmethod
    def create_comentario_repository(session=None):
        from app.repositories.comentario_repository import ComentarioRepository
        if session is None:
            session = DatabaseFactory.get_session()
        return ComentarioRepository(session)
