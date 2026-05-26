from datetime import datetime
from app.factories.app_factory import db

publicacion_likes = db.Table('publicacion_likes',
    db.Column('id_usuario', db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True),
    db.Column('id_publicacion', db.Integer, db.ForeignKey('publicaciones.id_publicacion', ondelete='CASCADE'), primary_key=True)
)

class Publicacion(db.Model):
    """Modelo de Publicación (Post) - GamesSphere"""
    __tablename__ = 'publicaciones'
    
    id_publicacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(255))
    juego = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    promocionada = db.Column(db.Boolean, default=False)
    boost_tipo = db.Column(db.String(20), nullable=True)
    boost_hasta = db.Column(db.DateTime, nullable=True)
    
    # Relación con el usuario (autor)
    autor = db.relationship('Usuario', backref=db.backref('publicaciones', lazy=True))
    
    # Relación de likes
    usuarios_likes = db.relationship('Usuario', secondary=publicacion_likes, lazy='subquery',
        backref=db.backref('publicaciones_likeadas', lazy=True))

    comentarios = db.relationship(
        'Comentario',
        backref='publicacion',
        lazy=True,
        order_by='Comentario.fecha_creacion',
        cascade='all, delete-orphan',
    )

    @property
    def likes(self):
        try:
            return len(self.usuarios_likes)
        except Exception:
            return 0

    def is_liked_by(self, usuario):
        if usuario is None:
            return False
        if hasattr(usuario, 'is_authenticated') and not usuario.is_authenticated:
            return False
        uid = getattr(usuario, 'id_usuario', None)
        if uid is None:
            return False
        return any(u.id_usuario == uid for u in self.usuarios_likes)
    
    def __repr__(self):
        return f'<Publicacion {self.id_publicacion} por User {self.id_usuario}>'
