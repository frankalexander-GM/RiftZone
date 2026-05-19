from app.factories.app_factory import db
from datetime import datetime

class MensajeChat(db.Model):
    __tablename__ = 'mensajes_chat'
    
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(500), nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    # Relación con el usuario para poder acceder a su foto y nombre
    usuario = db.relationship('Usuario', backref=db.backref('mensajes_chat', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'contenido': self.contenido,
            'fecha_envio': self.fecha_envio.strftime('%H:%M'),
            'usuario_nombre': self.usuario.username,
            'usuario_foto': self.usuario.foto_perfil or 'https://ui-avatars.com/api/?name=' + self.usuario.username
        }
