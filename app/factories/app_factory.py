from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Inicializar extensiones
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """
    Fábrica de aplicaciones Flask - RiftZone
    """
    import os
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(basedir, 'static'))
    
    from app.config.config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Inicia sesión para acceder a RiftZone.'
    login_manager.login_message_category = 'info'
    
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    register_blueprints(app)
    register_error_handlers(app)
    register_template_filters(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
        
    # Crear tablas faltantes automáticamente al arrancar
    with app.app_context():
        try:
            from app.models.usuario import Usuario, Notificacion
            from app.models.chat import MensajeChat
            from app.models.chat_comunidad import MensajeComunidad
            from app.models.clan import Clan, MiembroClan, SolicitudClan, MensajeClan, PublicacionClan
            from sqlalchemy import text
            
            # Actualizar tabla de usuarios con nuevos campos de la Fase 1
            with db.engine.connect() as conn:
                columnas = [
                    "ALTER TABLE usuarios ADD COLUMN pais VARCHAR(50)",
                    "ALTER TABLE usuarios ADD COLUMN estado_personalizado VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN twitch VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN kick VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN youtube VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN discord VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN steam VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN titulo_perfil VARCHAR(50) DEFAULT 'Gamer'"
                ]
                for col_sql in columnas:
                    try:
                        conn.execute(text(col_sql))
                        conn.commit()
                    except Exception:
                        pass # La columna ya existe
                
            # Limpiar mensajes y publicaciones huérfanas de clanes borrados en sesiones anteriores
            with db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("DELETE FROM mensajes_clan WHERE clan_id NOT IN (SELECT id_clan FROM clanes)"))
                conn.execute(text("DELETE FROM publicaciones_clan WHERE clan_id NOT IN (SELECT id_clan FROM clanes)"))
                conn.execute(text("DELETE FROM miembros_clan WHERE clan_id NOT IN (SELECT id_clan FROM clanes)"))
                conn.commit()
            
            db.create_all()
            MensajeComunidad.__table__.create(db.engine, checkfirst=True)
                
            print("Tablas verificadas/creadas con éxito.")
        except Exception as e:
            print(f"\n====== ERROR GRAVE AL CREAR TABLAS ======\n{e}\n========================================\n")
    
    return app

def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación"""
    from app.controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.controllers.jugador import jugador_bp
    app.register_blueprint(jugador_bp, url_prefix='/jugador')
    
    from app.controllers.public import public_bp
    app.register_blueprint(public_bp)

    from app.controllers.chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    from app.controllers.clanes import clanes_bp
    app.register_blueprint(clanes_bp, url_prefix='/clanes')

def register_error_handlers(app):
    """Registrar manejadores de errores personalizados"""
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

def register_template_filters(app):
    """Registrar filtros personalizados para plantillas"""
    @app.template_filter('timeago')
    def timeago_filter(value):
        if value is None:
            return ""
        try:
            return value.strftime('%d/%m/%Y')
        except:
            return str(value)
