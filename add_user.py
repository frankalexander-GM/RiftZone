import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.factories.app_factory import create_app, db
from app.models.usuario import Usuario

app = create_app('development')

with app.app_context():
    from app.factories.app_factory import bcrypt
    
    username = 'CyberNinja'
    if not Usuario.query.filter_by(username=username).first():
        u = Usuario(
            nombre='Cyber Ninja',
            username=username,
            email='ninja@riftzone.com',
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            biografia='🗡️ Sigilo y velocidad | Jugador de juegos de ritmo y hack n slash',
            foto_perfil='https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=200&auto=format&fit=crop',
            juegos_favoritos='Sekiro,Osu!'
        )
        db.session.add(u)
        db.session.commit()
        print(f"Usuario '{username}' creado exitosamente.")
    else:
        print(f"El usuario '{username}' ya existe.")
