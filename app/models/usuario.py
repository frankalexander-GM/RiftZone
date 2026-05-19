from datetime import datetime
from flask_login import UserMixin
from app.factories.app_factory import db

# Tabla de seguidores (many-to-many self-referential)
seguidores = db.Table('seguidores',
    db.Column('seguidor_id', db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True),
    db.Column('seguido_id', db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True)
)

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    
    id_notificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
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
    
    # Personalización e Integraciones (Fase 1)
    pais = db.Column(db.String(50))
    estado_personalizado = db.Column(db.String(100))
    twitch = db.Column(db.String(100))
    kick = db.Column(db.String(100))
    youtube = db.Column(db.String(100))
    discord = db.Column(db.String(100))
    steam = db.Column(db.String(100))
    titulo_perfil = db.Column(db.String(50), default='Gamer')
    
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
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def is_admin(self):
        return self.rol == 'admin'
    
    def is_jugador(self):
        return self.rol == 'jugador'

