from app.factories.app_factory import db
from datetime import datetime

class Clan(db.Model):
    __tablename__ = 'clanes'
    
    id_clan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    banner_url = db.Column(db.String(255), nullable=True)
    privacidad = db.Column(db.String(20), default='publico') # publico o privado
    nivel = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # El usuario creador
    lider_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    lider = db.relationship('Usuario', backref=db.backref('clanes_liderados', lazy=True))
    
    miembros = db.relationship('MiembroClan', backref='clan', lazy='dynamic', cascade='all, delete-orphan')
    solicitudes = db.relationship('SolicitudClan', backref='clan', lazy='dynamic', cascade='all, delete-orphan')

class MiembroClan(db.Model):
    __tablename__ = 'miembros_clan'
    
    id_miembro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clan_id = db.Column(db.Integer, db.ForeignKey('clanes.id_clan', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    rol = db.Column(db.String(20), default='miembro') # Puede ser: lider, oficial, miembro
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación para acceder a los datos del jugador fácilmente
    usuario = db.relationship('Usuario', backref=db.backref('membresias_clan', lazy='dynamic'))

class SolicitudClan(db.Model):
    __tablename__ = 'solicitudes_clan'
    
    id_solicitud = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clan_id = db.Column(db.Integer, db.ForeignKey('clanes.id_clan'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    estado = db.Column(db.String(20), default='pendiente') # pendiente, aceptada, rechazada
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref='solicitudes_clan')

class MensajeClan(db.Model):
    __tablename__ = 'mensajes_clan'
    
    id_mensaje = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clan_id = db.Column(db.Integer, db.ForeignKey('clanes.id_clan', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario')
    clan_rel = db.relationship('Clan', backref=db.backref('mensajes', lazy='dynamic', order_by='MensajeClan.fecha_envio.asc()', cascade='all, delete-orphan'))

class PublicacionClan(db.Model):
    __tablename__ = 'publicaciones_clan'
    
    id_publicacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clan_id = db.Column(db.Integer, db.ForeignKey('clanes.id_clan', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario')
    clan_rel = db.relationship('Clan', backref=db.backref('publicaciones', lazy='dynamic', order_by='PublicacionClan.fecha_creacion.desc()', cascade='all, delete-orphan'))
