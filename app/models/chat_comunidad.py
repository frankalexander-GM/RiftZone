from datetime import datetime
from app.factories.app_factory import db
from app.utils.avatar import avatar_url


class ReaccionMensajeComunidad(db.Model):
    __tablename__ = 'reacciones_mensaje_comunidad'
    id = db.Column(db.Integer, primary_key=True)
    mensaje_id = db.Column(db.Integer, db.ForeignKey('mensajes_comunidad.id', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('reacciones_comunidad', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'emoji': self.emoji,
        }


class MensajeComunidad(db.Model):
    __tablename__ = 'mensajes_comunidad'
    id = db.Column(db.Integer, primary_key=True)
    comunidad = db.Column(db.String(100), nullable=False, index=True)
    contenido = db.Column(db.String(500), nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('mensajes_comunidad', lazy=True))
    reacciones = db.relationship('ReaccionMensajeComunidad', backref='mensaje', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        u = self.usuario
        if not u:
            return {
                'id': self.id,
                'contenido': self.contenido,
                'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else '',
                'usuario_id': None,
                'usuario_nombre': 'Usuario',
                'usuario_username': 'usuario',
                'usuario_foto': avatar_url(None),
                'es_premium': False,
                'reacciones': [],
            }
        nombre = (u.nombre or u.username or 'Usuario').strip()
        return {
            'id': self.id,
            'contenido': self.contenido,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else '',
            'usuario_id': u.id_usuario,
            'usuario_nombre': nombre,
            'usuario_username': u.username or '',
            'usuario_foto': avatar_url(u.foto_perfil),
            'es_premium': bool(u.es_premium),
            'reacciones': [r.to_dict() for r in self.reacciones.all()],
        }
