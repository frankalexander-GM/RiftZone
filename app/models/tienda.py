from app.factories.app_factory import db
from datetime import datetime

class StoreItem(db.Model):
    __tablename__ = 'store_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # 'frame', 'background', 'title', 'badge'
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, default=0)  # cantidad disponible, 0 = sin stock
    
    # Estilos aplicados al equipar (marco, título, etc.)
    css_class = db.Column(db.String(500), nullable=True)
    color_hex = db.Column(db.String(20), nullable=True)

class UserInventory(db.Model):
    __tablename__ = 'user_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('store_items.id', ondelete='CASCADE'), nullable=False)
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_equipped = db.Column(db.Boolean, default=False)
    
    user = db.relationship('Usuario', backref=db.backref('inventario', lazy='dynamic'))
    item = db.relationship('StoreItem')
