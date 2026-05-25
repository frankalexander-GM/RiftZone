import os
import secrets
from datetime import timedelta

class Config:
    """Configuración base de la aplicación RiftZone"""
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'riftzone_secreto_desarrollo_12345'
    
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'riftzone.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webp'}
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_NAME = '__gs_session'
    WTF_CSRF_TIME_LIMIT = 3600
    
    ITEMS_PER_PAGE = 12
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'riftzone_dev.db')

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
