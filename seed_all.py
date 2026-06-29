import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.factories.app_factory import create_app, db
from app.models.usuario import Usuario, Notificacion, seguidores, seguidores_comunidad
from app.models.publicacion import Publicacion, Poll, PollOption, PollVote, publicacion_likes
from app.models.comentario import Comentario
from app.models.transaccion import Transaccion
from app.models.chat import MensajeChat
from app.models.chat_comunidad import MensajeComunidad
from app.models.mensaje_privado import MensajePrivado
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

app = create_app('default')

USERS_DATA = [
    {'username': 'alicegamer', 'nombre': 'Alice Gamer', 'email': 'alice@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 15000, 'nivel': 42, 'xp': 3200, 'xp_max': 5000, 'pais': 'MX', 'biografia': 'Gamer de corazón. Streamer en mis ratos libres.'},
    {'username': 'bobstream', 'nombre': 'Bob Stream', 'email': 'bob@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 22000, 'nivel': 55, 'xp': 4100, 'xp_max': 6000, 'pais': 'ES', 'biografia': 'Streamer profesional. 10k en Twitch.'},
    {'username': 'carlagames', 'nombre': 'Carla Games', 'email': 'carla@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 8900, 'nivel': 28, 'xp': 1500, 'xp_max': 3000, 'pais': 'AR', 'biografia': 'Jugadora competitiva de Valorant y CS2.'},
    {'username': 'davidpixel', 'nombre': 'David Pixel', 'email': 'david@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 5100, 'nivel': 19, 'xp': 800, 'xp_max': 2000, 'pais': 'CO', 'biografia': 'Indie lover y creador de contenido.'},
    {'username': 'elenanight', 'nombre': 'Elena Night', 'email': 'elena@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 32000, 'nivel': 70, 'xp': 5500, 'xp_max': 7000, 'pais': 'CL', 'biografia': 'Gamer nocturna. Platino en todo lo que juego.'},
    {'username': 'frank', 'nombre': 'Frank Gamer', 'email': 'frank@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 10075, 'nivel': 35, 'xp': 2800, 'xp_max': 4500, 'pais': 'US', 'biografia': 'Tryhard de League y Valorant.'},
    {'username': 'fryuk', 'nombre': 'Fry Uk', 'email': 'fryuk@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 7800, 'nivel': 22, 'xp': 1100, 'xp_max': 2500, 'pais': 'GB', 'biografia': 'Minecraft builder y redstone engineer.'},
    {'username': 'nexo000', 'nombre': 'Nexo', 'email': 'nexo@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 14500, 'nivel': 48, 'xp': 3900, 'xp_max': 5500, 'pais': 'BR', 'biografia': 'Rocket League champion. Casado con el boost.'},
    {'username': 'testuser', 'nombre': 'Test User', 'email': 'testuser@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 3000, 'nivel': 10, 'xp': 400, 'xp_max': 1000, 'pais': 'JP', 'biografia': 'Probando cosas nuevas cada día.'},
    {'username': 'RiftBot', 'nombre': 'RiftZone Bot', 'email': 'bot@riftzone.com', 'password': 'bot123', 'rol': 'admin', 'tokens': 999999, 'nivel': 99, 'xp': 0, 'xp_max': 1, 'pais': None, 'biografia': 'Bot oficial de RiftZone.'},
]

POSTS_DATA = [
    # (username, content, juego, promocionada, boost_tipo, boost_hasta_hours, imagen_url, video_archivo)
    ('alicegamer', 'Acabo de ganar mi primera partida competitiva en Valorant! Alguien para jugar ranked?', 'Valorant', True, 'rapido', 12, None, None),
    ('alicegamer', 'Nuevo récord personal en aim training: 98% precisión!', 'Valorant', False, None, 0, None, None),
    ('alicegamer', 'Alguien más jugó el nuevo evento de Fortnite? Está increíble!', 'Fortnite', True, 'mega', 48, None, None),
    ('bobstream', 'EN VIVO: Jugando League of Legends rankeds. Vengan a ver!', 'League of Legends', True, 'titan', 120, None, None),
    ('bobstream', 'Nueva build de Minecraft 1.21 lista! Alguien quiere explorar el nuevo bioma?', 'Minecraft', False, None, 0, None, None),
    ('bobstream', 'Review: El nuevo parche de CS2 mejoró el netcode notablemente.', 'Counter-Strike 2', False, None, 0, None, None),
    ('carlagames', 'Hice un clutch 1v5 en Valorant. Mejor partida de mi vida!', 'Valorant', True, 'mega', 72, None, None),
    ('carlagames', 'Alguien para ranked en Apex? Soy main Wraith con 4k kills.', 'Apex Legends', False, None, 0, None, None),
    ('carlagames', 'Mi setup gamer 2025: RTX 5090 + monitor OLED 240Hz.', 'Valorant', False, None, 0, 'https://picsum.photos/seed/setup/800/400', None),
    ('davidpixel', 'Hice un juego en 48 horas para la game jam! Descarguenlo gratis.', 'Minecraft', False, None, 0, 'https://picsum.photos/seed/jam/800/400', None),
    ('davidpixel', 'Pixel art tutorial: Cómo hacer sprites para tu juego.', 'Minecraft', False, None, 0, None, 'https://www.w3schools.com/html/mov_bbb.mp4'),
    ('elenanight', 'Platino conseguido en Elden Ring! Después de 200 horas.', 'Minecraft', True, 'rapido', 24, None, None),
    ('elenanight', 'Recomienden juegos de terror psicológico. Ya jugé todos los clásicos.', 'Fortnite', False, None, 0, None, None),
    ('elenanight', 'Mi colección de juegos físicos: 500+ títulos en estante.', 'Minecraft', True, 'mega', 48, 'https://picsum.photos/seed/coleccion/800/400', None),
    ('frank', 'Alguien juega League? Busco duo para ranked flex.', 'League of Legends', True, 'rapido', 12, None, None),
    ('frank', 'Mi mejor jugada en Rocket League!', 'Rocket League', False, None, 0, None, 'https://www.w3schools.com/html/mov_bbb.mp4'),
    ('fryuk', 'Construí una ciudad medieval en Minecraft. 300 horas de trabajo!', 'Minecraft', True, 'titan', 168, 'https://picsum.photos/seed/ciudad/800/400', None),
    ('fryuk', 'Tutorial: Cómo hacer una granja automática de XP en 1.21.', 'Minecraft', False, None, 0, None, None),
    ('nexo000', 'Campeón del torneo de Rocket League! 3-0 en la final.', 'Rocket League', True, 'mega', 72, None, 'https://www.w3schools.com/html/mov_bbb.mp4'),
    ('nexo000', 'Tips para mejorar tu mecánica en Rocket League: Rotaciones.', 'Rocket League', False, None, 0, None, None),
    ('testuser', 'Cuál es el mejor battle royale del momento?', 'Fortnite', False, None, 0, None, None),
    ('testuser', 'Probando el nuevo mapa de Valorant. Opiniones?', 'Valorant', False, None, 0, None, None),
    ('RiftBot', 'Bienvenidos a RiftZone! La comunidad gamer más grande.', 'Valorant', False, None, 0, None, None),
    ('RiftBot', 'Recuerden reclamar su recompensa diaria en la billetera!', 'Fortnite', False, None, 0, None, None),
]

COMMENTS_DATA = [
    (1, 'bobstream', 'Felicidades! A qué rango llegaste?'),
    (1, 'carlagames', 'Yo también estoy subiendo, agrégame!'),
    (2, 'elenanight', '98%? Pasas el aim train diario?'),
    (4, 'alicegamer', 'Ya voy para tu stream!'),
    (4, 'frank', 'Te sigo desde hace meses, eres crack.'),
    (7, 'alicegamer', 'Ese clutch fue una locura!'),
    (9, 'bobstream', 'Qué monitor recomiendas?'),
    (12, 'nexo000', 'Elden Ring es una obra maestra.'),
    (15, 'bobstream', 'Yo juego support, agregame: BobStream#LAS'),
    (17, 'alicegamer', '300 horas! Comparte fotos!'),
    (19, 'fryuk', 'Esa final fue increíble. Bien jugado!'),
    (23, 'alicegamer', 'Gracias RiftBot!'),
]

CHAT_MESSAGES_DATA = [
    ('alicegamer', 'Alguien para jugar algo?'),
    ('bobstream', 'En vivo en 10 minutos!'),
    ('carlagames', 'Alguien tiene el nuevo parche de Valorant?'),
    ('davidpixel', 'Subí un nuevo video a YouTube'),
    ('elenanight', 'Buenas noches gamers!'),
    ('frank', 'Qué juegos están viciando esta semana?'),
    ('fryuk', 'Minecraft 1.21 es lo mejor que ha pasado'),
    ('nexo000', 'Alguien para Rocket League rankeds?'),
    ('testuser', 'Probando juegos nuevos, recomienden algo'),
    ('RiftBot', 'Recuerden seguir las reglas del chat!'),
]

COMMUNITY_CHAT_DATA = {
    'Valorant': [('carlagames', 'Alguien para ranked?'), ('alicegamer', 'Yo! Agregame'), ('bobstream', 'Main Jett aquí')],
    'Minecraft': [('fryuk', 'Nueva granja automática lista'), ('davidpixel', 'Pasame el tutorial'), ('elenanight', 'Build enorme en progreso')],
    'League of Legends': [('frank', 'Duo ranked necesito'), ('nexo000', 'Que rol juegas?'), ('bobstream', 'MID main')],
    'Rocket League': [('nexo000', 'Alguien para entrenar mecánicas?'), ('alicegamer', 'Yo necesito práctica')],
    'Fortnite': [('testuser', 'Nuevo mapa está genial'), ('carlagames', 'Prefiero el capítulo anterior')],
}

PRIVATE_MESSAGES = [
    ('alicegamer', 'bobstream', 'Hola! Vi tu stream ayer, estuvo genial!'),
    ('bobstream', 'alicegamer', 'Gracias! Me alegra que te haya gustado :)'),
    ('carlagames', 'alicegamer', 'Quieres hacer duo para Valorant más tarde?'),
    ('alicegamer', 'carlagames', 'Claro! Te agrego en un rato.'),
    ('frank', 'nexo000', 'Buena partida ayer en Rocket League!'),
    ('nexo000', 'frank', 'Gracias! Jugamos de nuevo cuando quieras.'),
]

POLLS_DATA = [
    (21, 'Cuál es el mejor Battle Royale?', '24h', ['Fortnite', 'Warzone', 'Apex Legends', 'PUBG']),
]

PREGUNTAS = [
    'Qué juego están viciando esta semana?', 'Cuál es el mejor shooter?',
    'Recomienden un juego indie', 'PC o consola?',
    'Cuál fue el mejor juego del año?',
]

GAMES = ['Valorant', 'Minecraft', 'League of Legends', 'Rocket League', 'Fortnite', 'Apex Legends', 'Counter-Strike 2']

print("Seeding database...")

with app.app_context():
    existing_usernames = {u.username for u in Usuario.query.all()}
    existing_emails = {u.email for u in Usuario.query.all()}
    users = {}

    for ud in USERS_DATA:
        if ud['username'] in existing_usernames or ud['email'] in existing_emails:
            u = Usuario.query.filter_by(username=ud['username']).first() or Usuario.query.filter_by(email=ud['email']).first()
            for k, v in ud.items():
                if k not in ('password', 'username', 'email'):
                    setattr(u, k, v)
            users[ud['username']] = u
            print(f"  Updated user: {ud['username']}")
        else:
            u = Usuario(
                username=ud['username'], nombre=ud['nombre'], email=ud['email'],
                password=generate_password_hash(ud['password']), rol=ud['rol'],
                tokens=ud['tokens'], nivel=ud['nivel'], xp=ud['xp'], xp_max=ud['xp_max'],
                pais=ud['pais'], biografia=ud['biografia'],
                fecha_registro=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
            )
            db.session.add(u)
            db.session.flush()
            users[ud['username']] = u
            print(f"  Created user: {ud['username']}")

    db.session.commit()
    print(f"  Users: {len(users)}")

    user_list = list(users.values())
    non_bot = [u for u in user_list if u.username != 'RiftBot']

    for u in non_bot:
        followers = random.sample([x for x in non_bot if x.id_usuario != u.id_usuario], random.randint(1, min(4, len(non_bot)-1)))
        for f in followers:
            exists = db.session.execute(seguidores.select().where(
                (seguidores.c.seguidor_id == f.id_usuario) & (seguidores.c.seguido_id == u.id_usuario)
            )).first()
            if not exists:
                db.session.execute(seguidores.insert().values(seguidor_id=f.id_usuario, seguido_id=u.id_usuario))
    db.session.commit()
    print("  Follows created")

    for u in non_bot:
        coms = random.sample(GAMES, random.randint(1, 3))
        for c in coms:
            exists = db.session.execute(seguidores_comunidad.select().where(
                (seguidores_comunidad.c.usuario_id == u.id_usuario) & (seguidores_comunidad.c.comunidad == c)
            )).first()
            if not exists:
                db.session.execute(seguidores_comunidad.insert().values(usuario_id=u.id_usuario, comunidad=c))
    db.session.commit()
    print("  Community follows created")

    existing_posts = Publicacion.query.count()
    if existing_posts < 5:
        now = datetime.utcnow()
        for i, (uname, content, juego, promocionada, boost_tipo, boost_hours, img, vid) in enumerate(POSTS_DATA):
            u = users[uname]
            p = Publicacion(
                id_usuario=u.id_usuario, contenido=content, juego=juego,
                promocionada=promocionada, boost_tipo=boost_tipo,
                boost_hasta=(now + timedelta(hours=boost_hours)) if promocionada else None,
                imagen_url=img, video_archivo=vid,
                fecha_creacion=now - timedelta(hours=len(POSTS_DATA)-i),
            )
            db.session.add(p)
            db.session.flush()

            all_users_except_author = [x for x in non_bot if x.id_usuario != u.id_usuario]
            likers = random.sample(all_users_except_author, min(random.randint(0, len(all_users_except_author)), 5))
            for lu in likers:
                exists = db.session.execute(publicacion_likes.select().where(
                    (publicacion_likes.c.id_publicacion == p.id_publicacion) &
                    (publicacion_likes.c.id_usuario == lu.id_usuario)
                )).first()
                if not exists:
                    db.session.execute(publicacion_likes.insert().values(id_publicacion=p.id_publicacion, id_usuario=lu.id_usuario))
            db.session.commit()

            if promocionada:
                tx = Transaccion(user_id=u.id_usuario, amount=-[100, 250, 600][['rapido','mega','titan'].index(boost_tipo)],
                                 tipo='egreso', description=f"Boost {boost_tipo.upper()} — publicación #{p.id_publicacion}")
                db.session.add(tx)
        print(f"  Posts: {len(POSTS_DATA)} created")
    else:
        print(f"  Posts: {existing_posts} already exist, skipping")

    existing_comment_count = Comentario.query.count()
    if existing_comment_count < 3:
        for post_idx, author_uname, text in COMMENTS_DATA:
            post = Publicacion.query.order_by(Publicacion.id_publicacion.asc()).offset(post_idx-1).first()
            if post:
                c = Comentario(id_publicacion=post.id_publicacion, id_usuario=users[author_uname].id_usuario, contenido=text)
                db.session.add(c)
        db.session.commit()
        print(f"  Comments: {len(COMMENTS_DATA)} created")
    else:
        print(f"  Comments: {existing_comment_count} already exist, skipping")

    existing_poll_count = Poll.query.count()
    if existing_poll_count == 0:
        for post_idx, pregunta, duracion, options in POLLS_DATA:
            post = Publicacion.query.order_by(Publicacion.id_publicacion.asc()).offset(post_idx-1).first()
            if post:
                poll = Poll(id_publicacion=post.id_publicacion, pregunta=pregunta, duracion=duracion)
                db.session.add(poll)
                db.session.flush()
                for texto in options:
                    db.session.add(PollOption(id_poll=poll.id_poll, texto=texto, votos=random.randint(0, 10)))
        db.session.commit()
        print("  Polls created")
    else:
        print(f"  Polls: {existing_poll_count} already exist, skipping")

    existing_chat_count = MensajeChat.query.count()
    if existing_chat_count < 3:
        for uname, text in CHAT_MESSAGES_DATA:
            m = MensajeChat(usuario_id=users[uname].id_usuario, contenido=text)
            db.session.add(m)
        db.session.commit()
        print(f"  Chat messages: {len(CHAT_MESSAGES_DATA)} created")
    else:
        print(f"  Chat messages: {existing_chat_count} already exist, skipping")

    existing_community_chat_count = MensajeComunidad.query.count()
    if existing_community_chat_count < 3:
        for comunidad, messages in COMMUNITY_CHAT_DATA.items():
            for uname, text in messages:
                m = MensajeComunidad(comunidad=comunidad, usuario_id=users[uname].id_usuario, contenido=text)
                db.session.add(m)
        db.session.commit()
        print("  Community chat messages created")
    else:
        print(f"  Community chat messages: {existing_community_chat_count} already exist, skipping")

    existing_pm_count = MensajePrivado.query.count()
    if existing_pm_count < 3:
        for emisor_uname, receptor_uname, text in PRIVATE_MESSAGES:
            m = MensajePrivado(emisor_id=users[emisor_uname].id_usuario, receptor_id=users[receptor_uname].id_usuario, contenido=text)
            db.session.add(m)
        db.session.commit()
        print("  Private messages created")
    else:
        print(f"  Private messages: {existing_pm_count} already exist, skipping")

    existing_notif_count = Notificacion.query.count()
    if existing_notif_count < 3:
        for u in non_bot[:5]:
            n = Notificacion(usuario_id=u.id_usuario, mensaje='Bienvenido a RiftZone! Completa tu perfil para empezar.',
                             icono='fas fa-star', tipo='sistema', enlace='/jugador/editar-perfil')
            db.session.add(n)
        for u in non_bot:
            seguidores_extra = [x for x in non_bot if x.id_usuario != u.id_usuario]
            for _ in range(random.randint(0, 2)):
                seg = random.choice(seguidores_extra) if seguidores_extra else None
                if seg:
                    n = Notificacion(usuario_id=u.id_usuario, mensaje=f'{seg.nombre or seg.username} empezó a seguirte.',
                                     icono='fas fa-user-plus', tipo='seguidor', enlace=f'/jugador/perfil/{seg.username}')
                    db.session.add(n)
        db.session.commit()
        print("  Notifications created")
    else:
        print(f"  Notifications: {existing_notif_count} already exist, skipping")

    existing_tx_count = Transaccion.query.count()
    if existing_tx_count < 3:
        for u in non_bot:
            if (u.tokens or 0) > 5000:
                tx = Transaccion(user_id=u.id_usuario, amount=(u.tokens or 0) - 1000, tipo='ingreso',
                                 description='Recompensa diaria RiftZone', created_at=datetime.utcnow() - timedelta(days=1))
                db.session.add(tx)
        db.session.commit()
        print("  Transactions created")
    else:
        print(f"  Transactions: {existing_tx_count} already exist, skipping")

    print("\nSeed complete!")
