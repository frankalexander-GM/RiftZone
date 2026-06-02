from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

# Inicializar extensiones
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
socketio = SocketIO()

def create_app(config_name='default'):
    import os
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    flask_app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(basedir, 'static'))
    
    from app.config.config import config
    flask_app.config.from_object(config[config_name])
    config[config_name].init_app(flask_app)
    
    db.init_app(flask_app)
    bcrypt.init_app(flask_app)
    login_manager.init_app(flask_app)
    migrate.init_app(flask_app, db)
    csrf.init_app(flask_app)
    socketio.init_app(flask_app, cors_allowed_origins="*")
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Inicia sesión para acceder a GamesSphere.'
    login_manager.login_message_category = 'info'
    
    flask_app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
    upload_folder = flask_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    register_blueprints(flask_app)
    register_error_handlers(flask_app)
    register_template_filters(flask_app)

    # Inicializar manejadores de SocketIO
    import app.services.socketio_events
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    
    @flask_app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
        
    # Crear tablas faltantes automáticamente al arrancar
    with flask_app.app_context():
        try:
            from app.models.usuario import Usuario, Notificacion
            from app.models.chat import MensajeChat
            from app.models.chat_comunidad import MensajeComunidad
            from app.models.clan import Clan, MiembroClan, SolicitudClan, MensajeClan, PublicacionClan
            from app.models.publicacion import Publicacion, publicacion_likes, Poll, PollOption, PollVote, Report, publicacion_oculta
            from app.models.comentario import Comentario
            from app.models.transaccion import Transaccion
            from app.models.tienda import StoreItem, UserInventory
            from app.models.mensaje_privado import MensajePrivado
            from sqlalchemy import text
            
            # Actualizar tabla de usuarios con nuevos campos
            with db.engine.connect() as conn:
                columnas = [
                    "ALTER TABLE usuarios ADD COLUMN pais VARCHAR(50)",
                    "ALTER TABLE usuarios ADD COLUMN disponibilidad VARCHAR(50)",
                    "ALTER TABLE usuarios ADD COLUMN plataformas VARCHAR(150)",
                    "ALTER TABLE usuarios ADD COLUMN estado_personalizado VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN twitch VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN kick VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN youtube VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN discord VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN steam VARCHAR(100)",
                    "ALTER TABLE usuarios ADD COLUMN titulo_perfil VARCHAR(50) DEFAULT 'Gamer'",
                    "ALTER TABLE usuarios ADD COLUMN membresia_tipo VARCHAR(50) DEFAULT 'ninguna'",
                    "ALTER TABLE usuarios ADD COLUMN marco_perfil VARCHAR(255)",
                    "ALTER TABLE usuarios ADD COLUMN ultima_recompensa_diaria DATE",
                    "ALTER TABLE publicaciones ADD COLUMN boost_tipo VARCHAR(20)",
                    "ALTER TABLE publicaciones ADD COLUMN boost_hasta DATETIME",
                    "ALTER TABLE publicaciones ADD COLUMN fijada BOOLEAN DEFAULT 0",
                ]
                for col_sql in columnas:
                    try:
                        conn.execute(text(col_sql))
                        conn.commit()
                    except Exception:
                        pass # La columna ya existe
                
                # Migrar tabla store_items: agregar columna stock si no existe
                try:
                    conn.execute(text("ALTER TABLE store_items ADD COLUMN stock INTEGER DEFAULT 0"))
                    conn.commit()
                    print("Columna 'stock' añadida a store_items.")
                except Exception:
                    pass  # Ya existe
                try:
                    conn.execute(text("ALTER TABLE store_items ADD COLUMN color_hex VARCHAR(20)"))
                    conn.commit()
                except Exception:
                    pass

                # Migrar tabla polls: agregar multiple_choice y allow_change si no existen
                try:
                    conn.execute(text("ALTER TABLE polls ADD COLUMN multiple_choice BOOLEAN DEFAULT 0"))
                    conn.commit()
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE polls ADD COLUMN allow_change BOOLEAN DEFAULT 0"))
                    conn.commit()
                except Exception:
                    pass

                # Migrar tabla polls: agregar hide_results y duracion
                try:
                    conn.execute(text("ALTER TABLE polls ADD COLUMN hide_results BOOLEAN DEFAULT 0"))
                    conn.commit()
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE polls ADD COLUMN duracion VARCHAR(20) DEFAULT '24h'"))
                    conn.commit()
                except Exception:
                    pass

                # Migrar transacciones: type → tipo
                try:
                    conn.execute(text("ALTER TABLE transacciones ADD COLUMN tipo VARCHAR(50)"))
                    conn.commit()
                    conn.execute(text("UPDATE transacciones SET tipo = type WHERE tipo IS NULL"))
                    conn.commit()
                    print("Columna 'tipo' añadida a transacciones y datos migrados desde 'type'.")
                except Exception:
                    pass  # Ya existe

            # Limpiar mensajes y publicaciones huérfanas de clanes borrados en sesiones anteriores
            with db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("DELETE FROM mensajes_clan WHERE clan_id NOT IN (SELECT id_clan FROM clanes)"))
                conn.execute(text("DELETE FROM publicaciones_clan WHERE clan_id NOT IN (SELECT id_clan FROM clanes)"))
                conn.execute(text("DELETE FROM miembros_clan WHERE clan_id NOT IN (SELECT id_clan FROM clanes)"))
                conn.commit()
            
            db.create_all()

            from app.utils.banner import DEFAULT_PROFILE_BANNER
            sin_banner = Usuario.query.filter(
                (Usuario.banner.is_(None)) | (Usuario.banner == '')
            ).all()
            if sin_banner:
                for u in sin_banner:
                    u.banner = DEFAULT_PROFILE_BANNER
                db.session.commit()
                
            print("Tablas verificadas/creadas con éxito.")
        except Exception as e:
            print(f"\n====== ERROR GRAVE AL CREAR TABLAS ======\n{e}\n========================================\n")
    
    return flask_app

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
    
    from app.controllers.billetera import billetera_bp
    app.register_blueprint(billetera_bp, url_prefix='/billetera')

    from app.controllers.tienda import tienda_bp
    app.register_blueprint(tienda_bp, url_prefix='/tienda')

    from app.controllers.mensajes import mensajes_bp
    app.register_blueprint(mensajes_bp, url_prefix='')  # /mensajes

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
    from app.utils.avatar import avatar_url as resolve_avatar_url
    from app.utils.banner import profile_banner_url

    @app.template_filter('user_banner')
    def user_banner_filter(user):
        if user is None:
            return profile_banner_url(None)
        if hasattr(user, 'is_authenticated') and not user.is_authenticated:
            return profile_banner_url(None)
        return profile_banner_url(getattr(user, 'banner', None))

    @app.template_filter('user_avatar')
    def user_avatar_filter(user):
        if user is None:
            return resolve_avatar_url(None)
        if hasattr(user, 'is_authenticated') and not user.is_authenticated:
            return resolve_avatar_url(None)
        return resolve_avatar_url(getattr(user, 'foto_perfil', None))

    @app.template_filter('timeago')
    def timeago_filter(value):
        if value is None:
            return ""
        try:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            if value.tzinfo is None:
                from datetime import timezone
                value = value.replace(tzinfo=timezone.utc)
            diff = now - value
            seconds = int(diff.total_seconds())
            if seconds < 60:
                return 'justo ahora'
            minutes = seconds // 60
            if minutes < 60:
                return f'hace {minutes} min'
            hours = minutes // 60
            if hours < 24:
                return f'hace {hours} h'
            days = hours // 24
            if days < 7:
                return f'hace {days} día{"s" if days != 1 else ""}'
            weeks = days // 7
            if weeks < 5:
                return f'hace {weeks} semana{"s" if weeks != 1 else ""}'
            return value.strftime('%d/%m/%Y')
        except:
            return str(value)

    @app.template_filter('nombre_estilo')
    def nombre_estilo_filter(user):
        from app.utils.cosmetics import estilo_nombre_usuario
        return estilo_nombre_usuario(user)

    @app.template_filter('nombre_display')
    def nombre_display_filter(user):
        from app.utils.cosmetics import texto_nombre_usuario
        return texto_nombre_usuario(user)
