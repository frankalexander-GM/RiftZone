from datetime import datetime
from app.factories.app_factory import db
from app.utils.avatar import avatar_url


class MensajeChat(db.Model):
    __tablename__ = 'mensajes_chat'
    
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(500), nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    # Relación con el usuario para poder acceder a su foto y nombre
    usuario = db.relationship('Usuario', backref=db.backref('mensajes_chat', lazy=True))
    
    def to_dict(self):
        u = self.usuario
        if not u:
            return {
                'id': self.id,
                'contenido': self.contenido,
                'fecha_envio': self.fecha_envio.strftime('%H:%M') if self.fecha_envio else '',
                'usuario_nombre': 'Usuario',
                'usuario_foto': avatar_url(None),
                'es_premium': False,
                'boost_color': None,
            }
        nombre = (u.nombre or u.username or 'Usuario').strip()
        from app.services.boost_service import color_nombre_boost
        boost_color = color_nombre_boost(u.id_usuario)
        return {
            'id': self.id,
            'contenido': self.contenido,
            'fecha_envio': self.fecha_envio.strftime('%H:%M') if self.fecha_envio else '',
            'usuario_nombre': nombre,
            'usuario_foto': avatar_url(u.foto_perfil),
            'es_premium': bool(u.es_premium),
            'boost_color': boost_color,
        }
