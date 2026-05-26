import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.factories.app_factory import create_app, db
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.comentario import Comentario

app = create_app('development')

with app.app_context():
    # Eliminar DB corrupta o antigua primero
    db_path = os.path.join(app.root_path, 'games_sphere_dev.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Base de datos antigua eliminada: {db_path}")
        except Exception as e:
            print(f"No se pudo eliminar la base de datos antigua: {e}")
            
    db.create_all()
    
    # Crear usuarios de prueba
    from app.factories.app_factory import bcrypt
    
    if not Usuario.query.filter_by(username='NexoBlade').first():
        u1 = Usuario(
            nombre='NexoBlade',
            username='NexoBlade',
            email='nexo@riftzone.com',
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            biografia='🎮 Gamer competitivo | Main Jett en Valorant | Streamer',
            foto_perfil='https://images.unsplash.com/photo-1618331835717-801e976710b2?q=80&w=200&auto=format&fit=crop',
            es_premium=True
        )
        db.session.add(u1)
    
    if not Usuario.query.filter_by(username='PixelCraft').first():
        u2 = Usuario(
            nombre='PixelCraft',
            username='PixelCraft',
            email='pixel@riftzone.com',
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            biografia='🧱 Builder profesional en Minecraft | Diseñador de mundos',
            foto_perfil='https://images.unsplash.com/photo-1614027164847-1b28cfe1df60?q=80&w=200&auto=format&fit=crop',
            juegos_favoritos='Minecraft,Fortnite'
        )
        db.session.add(u2)
    
    # Crear ítems de la tienda si no existen
    from app.models.tienda import StoreItem
    if StoreItem.query.count() == 0:
        items = [
            StoreItem(name="Marco Neón Cyber", category="frame", price=150, stock=10, image_url="https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=100&h=100&fit=crop", css_class="border: 3px solid #00ffcc; box-shadow: 0 0 10px #00ffcc;"),
            StoreItem(name="Marco Fuego Infernal", category="frame", price=300, stock=5, image_url="https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=100&h=100&fit=crop", css_class="border: 3px solid #ff4500; box-shadow: 0 0 15px #ff4500;"),
            StoreItem(name="Fondo Galaxia", category="background", price=500, stock=3, image_url="https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=400&h=200&fit=crop"),
            StoreItem(name="Fondo Pixel Art", category="background", price=250, stock=7, image_url="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400&h=200&fit=crop"),
            StoreItem(name="Título: Dios del Aim", category="title", price=1000, stock=2, css_class="color: #ff0055; font-weight: 900; text-shadow: 0 0 5px #ff0055;"),
            StoreItem(name="Título: Tryhard", category="title", price=200, stock=15, css_class="color: #ffff00; font-weight: bold;"),
        ]
        db.session.add_all(items)
        
    # Añadir columna 'stock' si no existe (para casos donde la DB ya estaba creada sin ella)
    from sqlalchemy import text
    try:
        db.session.execute(text('ALTER TABLE store_items ADD COLUMN stock INTEGER DEFAULT 0'))
        db.session.commit()
        print('Columna stock añadida a store_items (si no existía).')
    except Exception as e:
        # Probablemente la columna ya existe
        db.session.rollback()
        print('La columna stock ya existía o hubo un error al añadirla:', e)

    print("Base de datos RiftZone inicializada correctamente.")
    print("Usuarios de prueba creados: NexoBlade / PixelCraft (contraseña: 123456)")

