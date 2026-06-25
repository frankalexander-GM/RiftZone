from datetime import datetime
from app.factories.app_factory import db
from app.utils.avatar import avatar_url


class MensajePrivado(db.Model):
    __tablename__ = 'mensajes_privados'

    id_mensaje = db.Column(db.Integer, primary_key=True)
    emisor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    receptor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    contenido = db.Column(db.String(1000), nullable=False)
    imagen_url = db.Column(db.String(500), nullable=True)
    leido = db.Column(db.Boolean, default=False)
    leido_en = db.Column(db.DateTime, nullable=True)
    editado = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    emisor = db.relationship('Usuario', foreign_keys=[emisor_id], backref=db.backref('mensajes_enviados', lazy='dynamic'))
    receptor = db.relationship('Usuario', foreign_keys=[receptor_id], backref=db.backref('mensajes_recibidos', lazy='dynamic'))
    reacciones = db.relationship('ReaccionMensaje', backref='mensaje', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, desde_el_punto_de_vista=None):
        u = self.emisor if desde_el_punto_de_vista != self.receptor_id else self.receptor
        nombre = (u.nombre or u.username or 'Usuario').strip()
        return {
            'id': self.id_mensaje,
            'contenido': self.contenido,
            'imagen_url': self.imagen_url,
            'fecha': self.creado_en.strftime('%H:%M') if self.creado_en else '',
            'fecha_completa': self.creado_en.strftime('%d/%m/%Y %H:%M') if self.creado_en else '',
            'emisor_id': self.emisor_id,
            'receptor_id': self.receptor_id,
            'leido': self.leido,
            'leido_en': self.leido_en.isoformat() if self.leido_en else None,
            'editado': self.editado,
            'emisor_nombre': nombre,
            'emisor_foto': avatar_url(u.foto_perfil),
            'es_premium': bool(u.es_premium),
            'reacciones': [r.to_dict() for r in self.reacciones.all()],
        }


class ReaccionMensaje(db.Model):
    __tablename__ = 'reacciones_mensaje'

    id_reaccion = db.Column(db.Integer, primary_key=True)
    mensaje_id = db.Column(db.Integer, db.ForeignKey('mensajes_privados.id_mensaje', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    emoji = db.Column(db.String(10), nullable=False, default='❤️')
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref=db.backref('reacciones_mensajes', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id_reaccion,
            'mensaje_id': self.mensaje_id,
            'usuario_id': self.usuario_id,
            'emoji': self.emoji,
            'usuario_nombre': self.usuario.nombre or self.usuario.username,
        }
