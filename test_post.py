import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.factories.app_factory import create_app, db
from app.models.usuario import Usuario

app = create_app('development')

with app.app_context():
    try:
        from app.factories.service_factory import get_service_factory
        sf = get_service_factory()
        pub_service = sf.get_publicacion_service()
        
        user = Usuario.query.filter_by(username='NexoBlade').first()
        if not user:
            print("Usuario NexoBlade no existe")
            sys.exit(1)
            
        print("Intentando crear publicación...")
        pub = pub_service.crear_publicacion(
            id_usuario=user.id_usuario,
            contenido="Este es un post de prueba",
            juego="Valorant",
            imagen_url=""
        )
        print(f"Éxito: Publicación creada con ID {pub.id_publicacion}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
