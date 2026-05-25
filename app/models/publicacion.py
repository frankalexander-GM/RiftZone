from datetime import datetime
from app.factories.app_factory import db

publicacion_likes = db.Table('publicacion_likes',
    db.Column('id_usuario', db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True),
    db.Column('id_publicacion', db.Integer, db.ForeignKey('publicaciones.id_publicacion'), primary_key=True)
)

class Publicacion(db.Model):
    """Modelo de Publicación (Post) - RiftZone"""
    __tablename__ = 'publicaciones'
    
    id_publicacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(255))
    juego = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con el usuario (autor)
    autor = db.relationship('Usuario', backref=db.backref('publicaciones', lazy=True))
    
    # Relación de likes
    usuarios_likes = db.relationship('Usuario', secondary=publicacion_likes, lazy='subquery',
        backref=db.backref('publicaciones_likeadas', lazy=True))
    
    @property
    def likes(self):
        try:
            return len(self.usuarios_likes)
        except:
            return 0
    
    def __repr__(self):
        return f'<Publicacion {self.id_publicacion} por User {self.id_usuario}>'
