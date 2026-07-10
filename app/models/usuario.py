from datetime import datetime, date, timezone
from flask_login import UserMixin
from app.factories.app_factory import db

# Tabla de seguidores (many-to-many self-referential)
seguidores = db.Table('seguidores',
    db.Column('seguidor_id', db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True),
    db.Column('seguido_id', db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True)
)

# Tabla de seguidores de comunidades
seguidores_comunidad = db.Table('seguidores_comunidad',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True),
    db.Column('comunidad', db.String(100), primary_key=True)
)

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    
    id_notificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    icono = db.Column(db.String(50), default='fas fa-bell')
    enlace = db.Column(db.String(255), nullable=True)
    tipo = db.Column(db.String(50), default='sistema')
    leido = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref=db.backref('notificaciones', lazy='dynamic', order_by='Notificacion.fecha_creacion.desc()'))

class Usuario(UserMixin, db.Model):
    """Modelo de Usuario - RiftZone"""
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='jugador')
    biografia = db.Column(db.Text)
    foto_perfil = db.Column(db.String(255))
    banner = db.Column(db.String(255))
    nivel = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    xp_max = db.Column(db.Integer, default=5000)
    estado = db.Column(db.String(20), default='online')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    es_premium = db.Column(db.Boolean, default=False)
    juegos_favoritos = db.Column(db.String(255))
    tokens = db.Column(db.Integer, default=0)
    ultima_recompensa_diaria = db.Column(db.Date, nullable=True)
    chat_ultimo_visto = db.Column(db.Integer, default=0)
    
    # Personalización e Integraciones (Fase 1)
    pais = db.Column(db.String(50))
    disponibilidad = db.Column(db.String(50))
    plataformas = db.Column(db.String(150))
    estado_personalizado = db.Column(db.String(100))
    twitch = db.Column(db.String(100))
    kick = db.Column(db.String(100))
    youtube = db.Column(db.String(100))
    discord = db.Column(db.String(100))
    steam = db.Column(db.String(100))
    titulo_perfil = db.Column(db.String(50), default='Gamer')
    membresia_tipo = db.Column(db.String(50), default='ninguna')
    marco_perfil = db.Column(db.String(255), nullable=True)
    
    # Relación de seguidores
    siguiendo = db.relationship(
        'Usuario', secondary=seguidores,
        primaryjoin=(seguidores.c.seguidor_id == id_usuario),
        secondaryjoin=(seguidores.c.seguido_id == id_usuario),
        backref=db.backref('seguidores_list', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def get_id(self):
        return str(self.id_usuario)
    
    def seguir(self, usuario):
        if not self.esta_siguiendo(usuario):
            self.siguiendo.append(usuario)
    
    def dejar_de_seguir(self, usuario):
        if self.esta_siguiendo(usuario):
            self.siguiendo.remove(usuario)
    
    @property
    def num_seguidores(self):
        try:
            return self.seguidores_list.count()
        except:
            return 0
    
    @property
    def num_siguiendo(self):
        try:
            return self.siguiendo.count()
        except:
            return 0
    
    def esta_siguiendo(self, usuario):
        try:
            return self.siguiendo.filter(seguidores.c.seguido_id == usuario.id_usuario).count() > 0
        except:
            return False

    def seguir_comunidad(self, comunidad):
        if not self.esta_siguiendo_comunidad(comunidad):
            db.session.execute(seguidores_comunidad.insert().values(usuario_id=self.id_usuario, comunidad=comunidad))

    def dejar_seguir_comunidad(self, comunidad):
        if self.esta_siguiendo_comunidad(comunidad):
            db.session.execute(seguidores_comunidad.delete().where(
                db.and_(seguidores_comunidad.c.usuario_id == self.id_usuario,
                        seguidores_comunidad.c.comunidad == comunidad)
            ))

    def esta_siguiendo_comunidad(self, comunidad):
        try:
            return db.session.query(seguidores_comunidad).filter(
                seguidores_comunidad.c.usuario_id == self.id_usuario,
                seguidores_comunidad.c.comunidad == comunidad
            ).count() > 0
        except:
            return False
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def is_admin(self):
        return self.rol == 'admin'
    
    def is_jugador(self):
        return self.rol == 'jugador'

    def is_invitado(self):
        return self.rol == 'invitado'

class PasswordResetCode(db.Model):
    """Códigos de verificación para recuperación de contraseña"""
    __tablename__ = 'password_reset_codes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    codigo = db.Column(db.String(10), nullable=False)
    usado = db.Column(db.Boolean, default=False)
    expira_en = db.Column(db.DateTime, nullable=False)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = db.relationship('Usuario', backref=db.backref('reset_codes', lazy='dynamic'))


class Sugerencia(db.Model):
    __tablename__ = 'sugerencias'
    id_sugerencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='SET NULL'), nullable=True)
    juego_nombre = db.Column(db.String(200), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='sugerencias')

