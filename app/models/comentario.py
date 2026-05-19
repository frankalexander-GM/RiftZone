from datetime import datetime
from app.factories.app_factory import db

class Comentario(db.Model):
    """Modelo de Comentario - GamesSphere"""
    __tablename__ = 'comentarios'
    
    id_comentario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_publicacion = db.Column(db.Integer, db.ForeignKey('publicaciones.id_publicacion'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    autor = db.relationship('Usuario', backref=db.backref('comentarios_hechos', lazy=True))
    publicacion = db.relationship('Publicacion', backref=db.backref('comentarios', lazy=True))
    
    def __repr__(self):
        return f'<Comentario {self.id_comentario} en Post {self.id_publicacion}>'
