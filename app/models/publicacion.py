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
    fijada = db.Column(db.Boolean, default=False)
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

    # Relación con encuesta
    poll = db.relationship('Poll', backref='publicacion', uselist=False, lazy=True, cascade='all, delete-orphan')

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
    
    @property
    def is_poll(self):
        return self.poll is not None
    
    @property
    def is_tournament(self):
        return self.contenido and self.contenido.startswith('[Torneo]')
    
    def __repr__(self):
        return f'<Publicacion {self.id_publicacion} por User {self.id_usuario}>'


class Poll(db.Model):
    __tablename__ = 'polls'
    
    id_poll = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_publicacion = db.Column(db.Integer, db.ForeignKey('publicaciones.id_publicacion', ondelete='CASCADE'), nullable=False, unique=True)
    pregunta = db.Column(db.String(255), nullable=False)
    multiple_choice = db.Column(db.Boolean, default=False)
    allow_change = db.Column(db.Boolean, default=False)
    hide_results = db.Column(db.Boolean, default=False)
    duracion = db.Column(db.String(20), default='24h')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    options = db.relationship('PollOption', backref='poll', lazy=True, cascade='all, delete-orphan', order_by='PollOption.id_option')
    
    @property
    def total_votos(self):
        return sum(o.votos for o in self.options)
    
    def user_votes(self, usuario_id):
        """Returns list of option_ids the user voted for"""
        from app.factories.app_factory import db
        return [v.id_option for v in PollVote.query.filter(
            PollVote.id_option.in_([o.id_option for o in self.options]),
            PollVote.id_usuario == usuario_id
        ).all()]


class PollOption(db.Model):
    __tablename__ = 'poll_options'
    
    id_option = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_poll = db.Column(db.Integer, db.ForeignKey('polls.id_poll', ondelete='CASCADE'), nullable=False)
    texto = db.Column(db.String(200), nullable=False)
    votos = db.Column(db.Integer, default=0)
    
    voters = db.relationship('PollVote', backref='option', lazy='dynamic', cascade='all, delete-orphan')
    
    def has_voted(self, usuario_id):
        return self.voters.filter_by(id_usuario=usuario_id).count() > 0


class PollVote(db.Model):
    __tablename__ = 'poll_votes'
    
    id_voto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_option = db.Column(db.Integer, db.ForeignKey('poll_options.id_option', ondelete='CASCADE'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('id_option', 'id_usuario', name='uq_vote_option_user'),)
    
    usuario = db.relationship('Usuario', backref='poll_votes')


class Report(db.Model):
    __tablename__ = 'reports'
    id_reporte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_publicacion = db.Column(db.Integer, db.ForeignKey('publicaciones.id_publicacion', ondelete='CASCADE'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    motivo = db.Column(db.String(50), default='spam')
    descripcion = db.Column(db.Text, nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    resuelto = db.Column(db.Boolean, default=False)


publicacion_oculta = db.Table('publicacion_oculta',
    db.Column('id_usuario', db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True),
    db.Column('id_publicacion', db.Integer, db.ForeignKey('publicaciones.id_publicacion', ondelete='CASCADE'), primary_key=True),
)
