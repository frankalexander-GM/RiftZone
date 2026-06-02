from datetime import datetime
from app.factories.app_factory import db
from app.utils.avatar import avatar_url


class MensajePrivado(db.Model):
    __tablename__ = 'mensajes_privados'

    id_mensaje = db.Column(db.Integer, primary_key=True)
    emisor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    receptor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    contenido = db.Column(db.String(1000), nullable=False)
    leido = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    emisor = db.relationship('Usuario', foreign_keys=[emisor_id], backref=db.backref('mensajes_enviados', lazy='dynamic'))
    receptor = db.relationship('Usuario', foreign_keys=[receptor_id], backref=db.backref('mensajes_recibidos', lazy='dynamic'))

    def to_dict(self, desde_el_punto_de_vista=None):
        u = self.emisor if desde_el_punto_de_vista != self.receptor_id else self.receptor
        nombre = (u.nombre or u.username or 'Usuario').strip()
        from app.services.boost_service import color_nombre_boost
        boost_color = color_nombre_boost(u.id_usuario)
        return {
            'id': self.id_mensaje,
            'contenido': self.contenido,
            'fecha': self.creado_en.strftime('%H:%M') if self.creado_en else '',
            'fecha_completa': self.creado_en.strftime('%d/%m/%Y %H:%M') if self.creado_en else '',
            'emisor_id': self.emisor_id,
            'receptor_id': self.receptor_id,
            'leido': self.leido,
            'emisor_nombre': nombre,
            'emisor_foto': avatar_url(u.foto_perfil),
            'boost_color': boost_color,
            'es_premium': bool(u.es_premium),
        }