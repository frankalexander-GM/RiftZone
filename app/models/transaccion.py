from datetime import datetime
from app.factories.app_factory import db

class Transaccion(db.Model):
    """Modelo de Transacción (Billetera / RiftCoins) - GamesSphere"""
    __tablename__ = 'transacciones'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(50), nullable=False) # 'ingreso' o 'egreso'
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref=db.backref('transacciones', lazy='dynamic', order_by='Transaccion.created_at.desc()'))
    
    def __repr__(self):
        return f'<Transaccion {self.id}: {self.amount} RiftCoins ({self.tipo})>'
