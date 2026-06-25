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
                'usuario_username': 'usuario',
                'usuario_foto': avatar_url(None),
                'es_premium': False,
            }
        nombre = (u.nombre or u.username or 'Usuario').strip()
        return {
            'id': self.id,
            'contenido': self.contenido,
            'fecha_envio': self.fecha_envio.strftime('%H:%M') if self.fecha_envio else '',
            'usuario_nombre': nombre,
            'usuario_username': u.username or '',
            'usuario_foto': avatar_url(u.foto_perfil),
            'es_premium': bool(u.es_premium),
        }
