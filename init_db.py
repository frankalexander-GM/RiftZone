import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.factories.app_factory import create_app, db
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.comentario import Comentario

app = create_app('development')

with app.app_context():
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
    
    db.session.commit()
    print("Base de datos RiftZone inicializada correctamente.")
    print("Usuarios de prueba creados: NexoBlade / PixelCraft (contraseña: 123456)")

