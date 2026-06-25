import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.factories.app_factory import create_app, db
from app.models.usuario import Usuario, seguidores
from app.models.publicacion import Publicacion, Poll, PollOption, publicacion_likes
from datetime import datetime

app = create_app('default')
with app.app_context():
    users = {u.username: u for u in Usuario.query.all()}
    frank = users.get('frank')
    fryuk = users.get('fryuk')
    nexo = users.get('nexo000')
    testuser = users.get('testuser')
    riftbot = users.get('RiftBot')

    if not all([frank, fryuk, nexo, testuser, riftbot]):
        print("Missing users, creating RiftBot...")
        from werkzeug.security import generate_password_hash
        if not riftbot:
            riftbot = Usuario(
                username='RiftBot', nombre='RiftZone Bot',
                email='bot@riftzone.com', rol='admin',
                password=generate_password_hash('bot123')
            )
            db.session.add(riftbot)
            db.session.flush()

    # 1. Make frank follow fryuk
    existing = db.session.execute(
        seguidores.select().where(
            (seguidores.c.seguidor_id == frank.id_usuario) &
            (seguidores.c.seguido_id == fryuk.id_usuario)
        )
    ).first()
    if not existing:
        db.session.execute(
            seguidores.insert().values(seguidor_id=frank.id_usuario, seguido_id=fryuk.id_usuario)
        )
        print("Frank now follows fryuk")

    # 2. Delete old sample posts
    Publicacion.query.filter(Publicacion.contenido.like('[Sample]%')).delete(synchronize_session=False)
    db.session.flush()

    # 3. Create Para ti / regular post - by frank
    p1 = Publicacion(
        id_usuario=frank.id_usuario, contenido='[Sample] Acabo de ganar mi primera partida competitiva en Valorant! Alguien para jugar ranked?',
        juego='Valorant', fecha_creacion=datetime.utcnow()
    )
    db.session.add(p1)
    db.session.flush()

    # 4. Create post by fryuk (appears in Siguiendo for frank)
    p2 = Publicacion(
        id_usuario=fryuk.id_usuario, contenido='[Sample] Nueva build de Minecraft 1.21 lista! Alguien quiere explorar el nuevo bioma?',
        juego='Minecraft', fecha_creacion=datetime.utcnow()
    )
    db.session.add(p2)
    db.session.flush()

    # 5. Create popular post - by nexo + many likes
    p3 = Publicacion(
        id_usuario=nexo.id_usuario, contenido='[Sample] Hice un clutch 1v5 en League of Legends. Mejor partida de mi vida!',
        juego='League of Legends', fecha_creacion=datetime.utcnow()
    )
    db.session.add(p3)
    db.session.flush()

    # Add likes from all users
    for uid in [frank.id_usuario, fryuk.id_usuario, testuser.id_usuario, riftbot.id_usuario]:
        existing_like = db.session.execute(
            publicacion_likes.select().where(
                (publicacion_likes.c.id_publicacion == p3.id_publicacion) &
                (publicacion_likes.c.id_usuario == uid)
            )
        ).first()
        if not existing_like:
            db.session.execute(
                publicacion_likes.insert().values(id_publicacion=p3.id_publicacion, id_usuario=uid)
            )
    print("Popular post created with 4 likes")

    # 6. Create poll post
    p5 = Publicacion(
        id_usuario=testuser.id_usuario, contenido='[Sample] Cual es el mejor battle royale del momento?',
        juego='Fortnite', fecha_creacion=datetime.utcnow()
    )
    db.session.add(p5)
    db.session.flush()

    poll = Poll(id_publicacion=p5.id_publicacion, pregunta='Cual es el mejor Battle Royale?', duracion='48h')
    db.session.add(poll)
    db.session.flush()

    for texto in ['Fortnite', 'Warzone', 'Apex Legends', 'PUBG']:
        db.session.add(PollOption(id_poll=poll.id_poll, texto=texto, votos=0))
    print("Poll post created with 4 options")

    # 8. Create video post (uses imagen_url as video fallback)
    p6 = Publicacion(
        id_usuario=nexo.id_usuario, contenido='[Sample] Mi mejor jugada en Rocket League!',
        juego='Rocket League', imagen_url='https://www.w3schools.com/html/mov_bbb.mp4',
        video_archivo='https://www.w3schools.com/html/mov_bbb.mp4',
        fecha_creacion=datetime.utcnow()
    )
    db.session.add(p6)
    db.session.flush()
    print("Video post created")

    db.session.commit()
    print("\nDone! Created 6 sample posts for all sections.")
