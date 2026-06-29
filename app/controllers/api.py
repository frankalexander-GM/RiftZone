from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, current_user
from app.factories.app_factory import db
from app.models.usuario import Usuario, Notificacion
from app.models.publicacion import Publicacion
from app.models.comentario import Comentario
from app.models.transaccion import Transaccion
from app.models.chat import MensajeChat
from app.models.chat_comunidad import MensajeComunidad
from app.models.mensaje_privado import MensajePrivado
from datetime import datetime
from werkzeug.security import check_password_hash
import uuid

api_bp = Blueprint('api', __name__, url_prefix='/api')

_api_tokens = {}

def _get_user():
    if current_user and current_user.is_authenticated:
        return current_user
    auth = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    uid = _api_tokens.get(auth)
    if uid:
        return Usuario.query.get(uid)
    return None

def _serialize(obj, excludes=None):
    excludes = excludes or []
    d = {}
    for col in getattr(obj, '__table__', obj).columns if hasattr(obj, '__table__') else {}:
        if col.key in excludes:
            continue
        v = getattr(obj, col.key)
        if isinstance(v, datetime):
            v = v.isoformat()
        d[col.key] = v
    return d

@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '')
    password = data.get('password', '')
    user = Usuario.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401
    login_user(user)
    token = str(uuid.uuid4())
    _api_tokens[token] = user.id_usuario
    return jsonify({'success': True, 'token': token, 'user': _serialize(user, excludes=['password'])})

@api_bp.route('/logout', methods=['POST'])
def api_logout():
    auth = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    _api_tokens.pop(auth, None)
    logout_user()
    return jsonify({'success': True})

def _require_auth():
    user = _get_user()
    if not user:
        return jsonify({'success': False, 'error': 'No autenticado'}), 401
    return None

def _model_to_dict(obj):
    if obj is None: return None
    d = {}
    for col in obj.__table__.columns:
        v = getattr(obj, col.name)
        if isinstance(v, datetime):
            v = v.isoformat()
        d[col.name] = v
    return d

def _paginate(q, page, per_page=20):
    p = q.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'data': [_model_to_dict(r) for r in p.items],
        'page': p.page, 'per_page': p.per_page,
        'total': p.total, 'pages': p.pages,
    }

# ─────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────
@api_bp.route('/usuarios', methods=['GET'])
@api_bp.route('/usuarios/<int:id_usuario>', methods=['GET'])
def api_get_usuarios(id_usuario=None):
    if id_usuario:
        u = Usuario.query.get(id_usuario)
        if not u: return jsonify({'error': 'No encontrado'}), 404
        return jsonify(_model_to_dict(u, excludes=['password']))
    page = request.args.get('page', 1, type=int)
    q = Usuario.query.order_by(Usuario.username.asc())
    return jsonify(_paginate(q, page))

@api_bp.route('/usuarios', methods=['POST'])
def api_create_usuario():
    data = request.get_json(silent=True) or {}
    for f in ('username', 'email', 'password', 'nombre'):
        if f not in data:
            return jsonify({'error': f'Campo requerido: {f}'}), 400
    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username ya existe'}), 409
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya existe'}), 409
    from werkzeug.security import generate_password_hash
    u = Usuario(
        username=data['username'], email=data['email'],
        nombre=data['nombre'],
        password=generate_password_hash(data['password']),
        rol=data.get('rol', 'jugador'), tokens=data.get('tokens', 0),
        pais=data.get('pais'), biografia=data.get('biografia'),
    )
    db.session.add(u); db.session.commit()
    return jsonify(_model_to_dict(u, excludes=['password'])), 201

@api_bp.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def api_update_usuario(id_usuario):
    auth_err = _require_auth()
    if auth_err: return auth_err
    u = Usuario.query.get(id_usuario)
    if not u: return jsonify({'error': 'No encontrado'}), 404
    current = _get_user()
    if current.id_usuario != u.id_usuario and current.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403
    data = request.get_json(silent=True) or {}
    for campo in ('nombre', 'biografia', 'pais', 'tokens', 'nivel', 'rol'):
        if campo in data:
            setattr(u, campo, data[campo])
    if 'password' in data and data['password']:
        from werkzeug.security import generate_password_hash
        u.password = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify(_model_to_dict(u, excludes=['password']))

@api_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def api_delete_usuario(id_usuario):
    auth_err = _require_auth()
    if auth_err: return auth_err
    u = Usuario.query.get(id_usuario)
    if not u: return jsonify({'error': 'No encontrado'}), 404
    current = _get_user()
    if current.id_usuario != u.id_usuario and current.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403
    db.session.delete(u); db.session.commit()
    return jsonify({'success': True})

# ─────────────────────────────────────────
# PUBLICACIONES
# ─────────────────────────────────────────
@api_bp.route('/publicaciones', methods=['GET'])
@api_bp.route('/publicaciones/<int:id>', methods=['GET'])
def api_get_publicaciones(id=None):
    if id:
        p = Publicacion.query.get(id)
        if not p: return jsonify({'error': 'No encontrado'}), 404
        return jsonify(_model_to_dict(p))
    page = request.args.get('page', 1, type=int)
    q = Publicacion.query.order_by(Publicacion.fecha_creacion.desc())
    if request.args.get('juego'):
        q = q.filter_by(juego=request.args['juego'])
    if request.args.get('id_usuario'):
        q = q.filter_by(id_usuario=int(request.args['id_usuario']))
    return jsonify(_paginate(q, page))

@api_bp.route('/publicaciones', methods=['POST'])
def api_create_publicacion():
    auth_err = _require_auth()
    if auth_err: return auth_err
    data = request.get_json(silent=True) or {}
    for f in ('contenido', 'juego'):
        if f not in data:
            return jsonify({'error': f'Campo requerido: {f}'}), 400
    p = Publicacion(
        id_usuario=_get_user().id_usuario, contenido=data['contenido'],
        juego=data['juego'], imagen_url=data.get('imagen_url'),
        video_archivo=data.get('video_archivo'),
    )
    db.session.add(p); db.session.commit()
    return jsonify(_model_to_dict(p)), 201

@api_bp.route('/publicaciones/<int:id>', methods=['PUT'])
def api_update_publicacion(id):
    auth_err = _require_auth()
    if auth_err: return auth_err
    p = Publicacion.query.get(id)
    if not p: return jsonify({'error': 'No encontrado'}), 404
    current = _get_user()
    if current.id_usuario != p.id_usuario and current.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403
    data = request.get_json(silent=True) or {}
    for campo in ('contenido', 'juego', 'imagen_url', 'video_archivo', 'promocionada'):
        if campo in data:
            setattr(p, campo, data[campo])
    db.session.commit()
    return jsonify(_model_to_dict(p))

@api_bp.route('/publicaciones/<int:id>', methods=['DELETE'])
def api_delete_publicacion(id):
    auth_err = _require_auth()
    if auth_err: return auth_err
    p = Publicacion.query.get(id)
    if not p: return jsonify({'error': 'No encontrado'}), 404
    current = _get_user()
    if current.id_usuario != p.id_usuario and current.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403
    db.session.delete(p); db.session.commit()
    return jsonify({'success': True})

# ─────────────────────────────────────────
# COMENTARIOS
# ─────────────────────────────────────────
@api_bp.route('/comentarios', methods=['GET'])
@api_bp.route('/comentarios/<int:id>', methods=['GET'])
def api_get_comentarios(id=None):
    if id:
        c = Comentario.query.get(id)
        if not c: return jsonify({'error': 'No encontrado'}), 404
        return jsonify(_model_to_dict(c))
    page = request.args.get('page', 1, type=int)
    q = Comentario.query.order_by(Comentario.fecha_creacion.desc())
    if request.args.get('id_publicacion'):
        q = q.filter_by(id_publicacion=int(request.args['id_publicacion']))
    return jsonify(_paginate(q, page))

@api_bp.route('/comentarios', methods=['POST'])
def api_create_comentario():
    auth_err = _require_auth()
    if auth_err: return auth_err
    data = request.get_json(silent=True) or {}
    for f in ('id_publicacion', 'contenido'):
        if f not in data:
            return jsonify({'error': f'Campo requerido: {f}'}), 400
    post = Publicacion.query.get(data['id_publicacion'])
    if not post: return jsonify({'error': 'Publicación no existe'}), 404
    c = Comentario(id_publicacion=post.id_publicacion, id_usuario=_get_user().id_usuario, contenido=data['contenido'])
    db.session.add(c); db.session.commit()
    return jsonify(_model_to_dict(c)), 201

@api_bp.route('/comentarios/<int:id>', methods=['DELETE'])
def api_delete_comentario(id):
    auth_err = _require_auth()
    if auth_err: return auth_err
    c = Comentario.query.get(id)
    if not c: return jsonify({'error': 'No encontrado'}), 404
    current = _get_user()
    if current.id_usuario != c.id_usuario and current.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403
    db.session.delete(c); db.session.commit()
    return jsonify({'success': True})

# ─────────────────────────────────────────
# TRANSACCIONES
# ─────────────────────────────────────────
@api_bp.route('/transacciones', methods=['GET'])
@api_bp.route('/transacciones/<int:id>', methods=['GET'])
def api_get_transacciones(id=None):
    if id:
        t = Transaccion.query.get(id)
        if not t: return jsonify({'error': 'No encontrado'}), 404
        return jsonify(_model_to_dict(t))
    page = request.args.get('page', 1, type=int)
    q = Transaccion.query.order_by(Transaccion.created_at.desc())
    if request.args.get('user_id'):
        q = q.filter_by(user_id=int(request.args['user_id']))
    return jsonify(_paginate(q, page))

@api_bp.route('/transacciones', methods=['POST'])
def api_create_transaccion():
    auth_err = _require_auth()
    if auth_err: return auth_err
    data = request.get_json(silent=True) or {}
    for f in ('user_id', 'amount', 'tipo', 'description'):
        if f not in data:
            return jsonify({'error': f'Campo requerido: {f}'}), 400
    t = Transaccion(user_id=data['user_id'], amount=data['amount'], tipo=data['tipo'], description=data['description'])
    user = Usuario.query.get(data['user_id'])
    if not user: return jsonify({'error': 'Usuario no existe'}), 404
    if data['tipo'] == 'egreso':
        user.tokens = (user.tokens or 0) - abs(data['amount'])
    else:
        user.tokens = (user.tokens or 0) + abs(data['amount'])
    db.session.add(t); db.session.commit()
    return jsonify(_model_to_dict(t)), 201

# ─────────────────────────────────────────
# NOTIFICACIONES
# ─────────────────────────────────────────
@api_bp.route('/notificaciones', methods=['GET'])
@api_bp.route('/notificaciones/<int:id>', methods=['GET'])
def api_get_notificaciones(id=None):
    if id:
        n = Notificacion.query.get(id)
        if not n: return jsonify({'error': 'No encontrado'}), 404
        return jsonify(_model_to_dict(n))
    page = request.args.get('page', 1, type=int)
    q = Notificacion.query.order_by(Notificacion.fecha_creacion.desc())
    if request.args.get('usuario_id'):
        q = q.filter_by(usuario_id=int(request.args['usuario_id']))
    return jsonify(_paginate(q, page))

@api_bp.route('/notificaciones/<int:id>', methods=['PUT'])
def api_leer_notificacion(id):
    auth_err = _require_auth()
    if auth_err: return auth_err
    n = Notificacion.query.get(id)
    if not n: return jsonify({'error': 'No encontrado'}), 404
    n.leido = request.get_json(silent=True).get('leido', True) if request.get_json(silent=True) else True
    db.session.commit()
    return jsonify(_model_to_dict(n))

@api_bp.route('/notificaciones/<int:id>', methods=['DELETE'])
def api_delete_notificacion(id):
    auth_err = _require_auth()
    if auth_err: return auth_err
    n = Notificacion.query.get(id)
    if not n: return jsonify({'error': 'No encontrado'}), 404
    current = _get_user()
    if current.id_usuario != n.usuario_id and current.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403
    db.session.delete(n); db.session.commit()
    return jsonify({'success': True})

# ─────────────────────────────────────────
# MENSAJES CHAT
# ─────────────────────────────────────────
@api_bp.route('/chat', methods=['GET'])
def api_get_chat():
    page = request.args.get('page', 1, type=int)
    q = MensajeChat.query.order_by(MensajeChat.fecha_envio.desc())
    return jsonify(_paginate(q, page))

@api_bp.route('/chat', methods=['POST'])
def api_create_chat():
    auth_err = _require_auth()
    if auth_err: return auth_err
    data = request.get_json(silent=True) or {}
    if 'contenido' not in data:
        return jsonify({'error': 'Campo requerido: contenido'}), 400
    m = MensajeChat(usuario_id=_get_user().id_usuario, contenido=data['contenido'])
    db.session.add(m); db.session.commit()
    return jsonify(_model_to_dict(m)), 201

# ─────────────────────────────────────────
# ESTADISTICAS
# ─────────────────────────────────────────
@api_bp.route('/estadisticas', methods=['GET'])
def api_estadisticas():
    return jsonify({
        'usuarios': Usuario.query.count(),
        'publicaciones': Publicacion.query.count(),
        'comentarios': Comentario.query.count(),
        'transacciones': Transaccion.query.count(),
        'notificaciones': Notificacion.query.count(),
        'mensajes_chat': MensajeChat.query.count(),
        'mensajes_comunidad': MensajeComunidad.query.count(),
        'mensajes_privados': MensajePrivado.query.count(),
    })

# ─────────────────────────────────────────
# COMUNIDADES (lista de juegos disponibles)
# ─────────────────────────────────────────
@api_bp.route('/comunidades', methods=['GET'])
def api_get_comunidades():
    from app.data.game_categories import get_game_categories
    cats = get_game_categories()
    result = []
    for cat in cats:
        for g in cat['juegos']:
            result.append({
                'nombre': g['nombre'],
                'categoria': cat['nombre'],
                'descripcion': g.get('desc', ''),
                'imagen': g.get('imagen', ''),
                'posts': Publicacion.query.filter_by(juego=g['nombre']).count(),
                'seguidores': db.session.execute(
                    db.text("SELECT COUNT(*) FROM seguidores_comunidad WHERE comunidad = :c"),
                    {'c': g['nombre']}
                ).scalar(),
            })
    return jsonify(result)

@api_bp.route('/seed', methods=['POST'])
def api_seed():
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    import random

    USERS_DATA = [
        {'username': 'alicegamer', 'nombre': 'Alice Gamer', 'email': 'alice@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 15000, 'nivel': 42, 'xp': 3200, 'xp_max': 5000, 'pais': 'MX', 'biografia': 'Gamer de corazon. Streamer en mis ratos libres.'},
        {'username': 'bobstream', 'nombre': 'Bob Stream', 'email': 'bob@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 22000, 'nivel': 55, 'xp': 4100, 'xp_max': 6000, 'pais': 'ES', 'biografia': 'Streamer profesional. 10k en Twitch.'},
        {'username': 'carlagames', 'nombre': 'Carla Games', 'email': 'carla@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 8900, 'nivel': 28, 'xp': 1500, 'xp_max': 3000, 'pais': 'AR', 'biografia': 'Jugadora competitiva de Valorant y CS2.'},
        {'username': 'davidpixel', 'nombre': 'David Pixel', 'email': 'david@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 5100, 'nivel': 19, 'xp': 800, 'xp_max': 2000, 'pais': 'CO', 'biografia': 'Indie lover y creador de contenido.'},
        {'username': 'elenanight', 'nombre': 'Elena Night', 'email': 'elena@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 32000, 'nivel': 70, 'xp': 5500, 'xp_max': 7000, 'pais': 'CL', 'biografia': 'Gamer nocturna. Platino en todo lo que juego.'},
        {'username': 'frank', 'nombre': 'Frank Gamer', 'email': 'frank@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 10075, 'nivel': 35, 'xp': 2800, 'xp_max': 4500, 'pais': 'US', 'biografia': 'Tryhard de League y Valorant.'},
        {'username': 'fryuk', 'nombre': 'Fry Uk', 'email': 'fryuk@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 7800, 'nivel': 22, 'xp': 1100, 'xp_max': 2500, 'pais': 'GB', 'biografia': 'Minecraft builder y redstone engineer.'},
        {'username': 'nexo000', 'nombre': 'Nexo', 'email': 'nexo@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 14500, 'nivel': 48, 'xp': 3900, 'xp_max': 5500, 'pais': 'BR', 'biografia': 'Rocket League champion. Casado con el boost.'},
        {'username': 'testuser', 'nombre': 'Test User', 'email': 'testuser@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 3000, 'nivel': 10, 'xp': 400, 'xp_max': 1000, 'pais': 'JP', 'biografia': 'Probando cosas nuevas cada dia.'},
        {'username': 'RiftBot', 'nombre': 'RiftZone Bot', 'email': 'bot@riftzone.com', 'password': 'bot123', 'rol': 'admin', 'tokens': 999999, 'nivel': 99, 'xp': 0, 'xp_max': 1, 'pais': None, 'biografia': 'Bot oficial de RiftZone.'},
    ]
    POSTS_DATA = [
        ('alicegamer', 'Acabo de ganar mi primera partida competitiva en Valorant! Alguien para jugar ranked?', 'Valorant', True, 'rapido', 12, None, None),
        ('alicegamer', 'Nuevo record personal en aim training: 98% precision!', 'Valorant', False, None, 0, None, None),
        ('alicegamer', 'Alguien mas jugo el nuevo evento de Fortnite? Esta increible!', 'Fortnite', True, 'mega', 48, None, None),
        ('bobstream', 'EN VIVO: Jugando League of Legends rankeds. Vengan a ver!', 'League of Legends', True, 'titan', 120, None, None),
        ('bobstream', 'Nueva build de Minecraft 1.21 lista! Alguien quiere explorar el nuevo bioma?', 'Minecraft', False, None, 0, None, None),
        ('bobstream', 'Review: El nuevo parche de CS2 mejoro el netcode notablemente.', 'Counter-Strike 2', False, None, 0, None, None),
        ('carlagames', 'Hice un clutch 1v5 en Valorant. Mejor partida de mi vida!', 'Valorant', True, 'mega', 72, None, None),
        ('carlagames', 'Alguien para ranked en Apex? Soy main Wraith con 4k kills.', 'Apex Legends', False, None, 0, None, None),
        ('carlagames', 'Mi setup gamer 2025: RTX 5090 + monitor OLED 240Hz.', 'Valorant', False, None, 0, 'https://picsum.photos/seed/setup/800/400', None),
        ('davidpixel', 'Hice un juego en 48 horas para la game jam! Descarguenlo gratis.', 'Minecraft', False, None, 0, 'https://picsum.photos/seed/jam/800/400', None),
        ('davidpixel', 'Pixel art tutorial: Como hacer sprites para tu juego.', 'Minecraft', False, None, 0, None, 'https://www.w3schools.com/html/mov_bbb.mp4'),
        ('elenanight', 'Platino conseguido en Elden Ring! Despues de 200 horas.', 'Minecraft', True, 'rapido', 24, None, None),
        ('elenanight', 'Recomienden juegos de terror psicologico. Ya juge todos los clasicos.', 'Fortnite', False, None, 0, None, None),
        ('elenanight', 'Mi coleccion de juegos fisicos: 500+ titulos en estante.', 'Minecraft', True, 'mega', 48, 'https://picsum.photos/seed/coleccion/800/400', None),
        ('frank', 'Alguien juega League? Busco duo para ranked flex.', 'League of Legends', True, 'rapido', 12, None, None),
        ('frank', 'Mi mejor jugada en Rocket League!', 'Rocket League', False, None, 0, None, 'https://www.w3schools.com/html/mov_bbb.mp4'),
        ('fryuk', 'Construi una ciudad medieval en Minecraft. 300 horas de trabajo!', 'Minecraft', True, 'titan', 168, 'https://picsum.photos/seed/ciudad/800/400', None),
        ('fryuk', 'Tutorial: Como hacer una granja automatica de XP en 1.21.', 'Minecraft', False, None, 0, None, None),
        ('nexo000', 'Campeon del torneo de Rocket League! 3-0 en la final.', 'Rocket League', True, 'mega', 72, None, 'https://www.w3schools.com/html/mov_bbb.mp4'),
        ('nexo000', 'Tips para mejorar tu mecanica en Rocket League: Rotaciones.', 'Rocket League', False, None, 0, None, None),
        ('testuser', 'Cual es el mejor battle royale del momento?', 'Fortnite', False, None, 0, None, None),
        ('testuser', 'Probando el nuevo mapa de Valorant. Opiniones?', 'Valorant', False, None, 0, None, None),
        ('RiftBot', 'Bienvenidos a RiftZone! La comunidad gamer mas grande.', 'Valorant', False, None, 0, None, None),
        ('RiftBot', 'Recuerden reclamar su recompensa diaria en la billetera!', 'Fortnite', False, None, 0, None, None),
    ]
    COMMENTS_DATA = [
        (1, 'bobstream', 'Felicidades! A que rango llegaste?'),
        (1, 'carlagames', 'Yo tambien estoy subiendo, agregame!'),
        (2, 'elenanight', '98%? Pasas el aim train diario?'),
        (4, 'alicegamer', 'Ya voy para tu stream!'),
        (4, 'frank', 'Te sigo desde hace meses, eres crack.'),
        (7, 'alicegamer', 'Ese clutch fue una locura!'),
        (9, 'bobstream', 'Que monitor recomiendas?'),
        (12, 'nexo000', 'Elden Ring es una obra maestra.'),
        (15, 'bobstream', 'Yo juego support, agregame: BobStream#LAS'),
        (17, 'alicegamer', '300 horas! Comparte fotos!'),
        (19, 'fryuk', 'Esa final fue increible. Bien jugado!'),
        (23, 'alicegamer', 'Gracias RiftBot!'),
    ]
    CHAT_MESSAGES_DATA = [
        'Alguien para jugar algo?', 'En vivo en 10 minutos!', 'Alguien tiene el nuevo parche de Valorant?',
        'Subi un nuevo video a YouTube', 'Buenas noches gamers!', 'Que juegos estan viciando esta semana?',
        'Minecraft 1.21 es lo mejor que ha pasado', 'Alguien para Rocket League rankeds?',
        'Probando juegos nuevos, recomienden algo', 'Recuerden seguir las reglas del chat!',
    ]
    GAMES = ['Valorant', 'Minecraft', 'League of Legends', 'Rocket League', 'Fortnite', 'Apex Legends', 'Counter-Strike 2']

    created = {'usuarios': 0, 'posts': 0, 'comentarios': 0, 'chat': 0, 'comunidad_mensajes': 0, 'privados': 0, 'notificaciones': 0, 'transacciones': 0}

    users = {}
    for ud in USERS_DATA:
        u = Usuario.query.filter_by(email=ud['email']).first()
        if not u:
            u = Usuario(username=ud['username'], nombre=ud['nombre'], email=ud['email'],
                        password=generate_password_hash(ud['password']), rol=ud['rol'],
                        tokens=ud['tokens'], nivel=ud['nivel'], xp=ud['xp'], xp_max=ud['xp_max'],
                        pais=ud['pais'], biografia=ud['biografia'])
            db.session.add(u)
            db.session.flush()
            created['usuarios'] += 1
        users[ud['username']] = u

    non_bot = [u for u in users.values() if u.username != 'RiftBot']

    for u in non_bot:
        followers = random.sample([x for x in non_bot if x.id_usuario != u.id_usuario], min(random.randint(1, 4), len(non_bot)-1))
        for f in followers:
            exists = db.session.execute(db.text("SELECT 1 FROM seguidores WHERE seguidor_id=:sid AND seguido_id=:sid2"),
                                        {'sid': f.id_usuario, 'sid2': u.id_usuario}).first()
            if not exists:
                db.session.execute(db.text("INSERT INTO seguidores (seguidor_id, seguido_id) VALUES (:sid, :sid2)"),
                                   {'sid': f.id_usuario, 'sid2': u.id_usuario})

    for u in non_bot:
        coms = random.sample(GAMES, random.randint(1, 3))
        for c in coms:
            exists = db.session.execute(db.text("SELECT 1 FROM seguidores_comunidad WHERE usuario_id=:uid AND comunidad=:c"),
                                        {'uid': u.id_usuario, 'c': c}).first()
            if not exists:
                db.session.execute(db.text("INSERT INTO seguidores_comunidad (usuario_id, comunidad) VALUES (:uid, :c)"),
                                   {'uid': u.id_usuario, 'c': c})

    now = datetime.utcnow()
    for i, (uname, content, juego, promocionada, boost_tipo, boost_hours, img, vid) in enumerate(POSTS_DATA):
        u = users[uname]
        p = Publicacion.query.filter_by(id_usuario=u.id_usuario, contenido=content).first()
        if not p:
            p = Publicacion(
                id_usuario=u.id_usuario, contenido=content, juego=juego,
                promocionada=promocionada,
                boost_tipo=boost_tipo,
                boost_hasta=(now + timedelta(hours=boost_hours)) if promocionada else None,
                imagen_url=img, video_archivo=vid,
                fecha_creacion=now - timedelta(hours=len(POSTS_DATA)-i),
            )
            db.session.add(p)
            db.session.flush()
            created['posts'] += 1
            all_except = [x for x in non_bot if x.id_usuario != u.id_usuario]
            if all_except:
                for lu in random.sample(all_except, min(random.randint(0, 5), len(all_except))):
                    exists = db.session.execute(db.text("SELECT 1 FROM publicacion_likes WHERE id_publicacion=:pid AND id_usuario=:uid"),
                                                {'pid': p.id_publicacion, 'uid': lu.id_usuario}).first()
                    if not exists:
                        db.session.execute(db.text("INSERT INTO publicacion_likes (id_publicacion, id_usuario) VALUES (:pid, :uid)"),
                                           {'pid': p.id_publicacion, 'uid': lu.id_usuario})
            if promocionada:
                boost_cost = [100, 250, 600][['rapido','mega','titan'].index(boost_tipo)]
                tx = Transaccion(user_id=u.id_usuario, amount=-boost_cost, tipo='egreso',
                                 description=f"Boost {boost_tipo.upper()} — publicacion #{p.id_publicacion}")
                db.session.add(tx)

    posts = Publicacion.query.order_by(Publicacion.id_publicacion.asc()).all()
    for post_idx, author_uname, text in COMMENTS_DATA:
        if post_idx <= len(posts):
            p = posts[post_idx-1]
            exists = Comentario.query.filter_by(id_publicacion=p.id_publicacion, contenido=text).first()
            if not exists:
                c = Comentario(id_publicacion=p.id_publicacion, id_usuario=users[author_uname].id_usuario, contenido=text)
                db.session.add(c)
                created['comentarios'] += 1

    for uname in list(users.keys())[:10]:
        m = MensajeChat(usuario_id=users[uname].id_usuario, contenido=CHAT_MESSAGES_DATA[list(users.keys()).index(uname)])
        db.session.add(m)
        created['chat'] += 1

    for c_idx, comunidad in enumerate(GAMES[:5]):
        for m_idx, uname in enumerate(list(users.keys())[:3]):
            idx = c_idx * 3 + m_idx
            if idx < 15:
                m = MensajeComunidad(comunidad=comunidad, usuario_id=users[uname].id_usuario,
                                     contenido=f"Mensaje en {comunidad} de {uname}")
                db.session.add(m)
                created['comunidad_mensajes'] += 1

    pm_pairs = [('alicegamer','bobstream'), ('bobstream','alicegamer'), ('carlagames','alicegamer'),
                ('alicegamer','carlagames'), ('frank','nexo000'), ('nexo000','frank')]
    pm_texts = [
        'Hola! Vi tu stream ayer, estuvo genial!', 'Gracias! Me alegra que te haya gustado :)',
        'Quieres hacer duo para Valorant mas tarde?', 'Claro! Te agrego en un rato.',
        'Buena partida ayer en Rocket League!', 'Gracias! Jugamos de nuevo cuando quieras.',
    ]
    for (e, r), txt in zip(pm_pairs, pm_texts):
        exists = MensajePrivado.query.filter_by(emisor_id=users[e].id_usuario, receptor_id=users[r].id_usuario, contenido=txt).first()
        if not exists:
            m = MensajePrivado(emisor_id=users[e].id_usuario, receptor_id=users[r].id_usuario, contenido=txt)
            db.session.add(m)
            created['privados'] += 1

    for u in non_bot[:5]:
        exists = Notificacion.query.filter_by(usuario_id=u.id_usuario, tipo='sistema').first()
        if not exists:
            n = Notificacion(usuario_id=u.id_usuario, mensaje='Bienvenido a RiftZone! Completa tu perfil para empezar.',
                             icono='fas fa-star', tipo='sistema', enlace='/jugador/editar-perfil')
            db.session.add(n)
            created['notificaciones'] += 1

    for u in non_bot:
        if (u.tokens or 0) > 5000:
            exists = Transaccion.query.filter_by(user_id=u.id_usuario, tipo='ingreso').first()
            if not exists:
                tx = Transaccion(user_id=u.id_usuario, amount=(u.tokens or 0) - 1000, tipo='ingreso',
                                 description='Recompensa diaria RiftZone', created_at=datetime.utcnow() - timedelta(days=1))
                db.session.add(tx)
                created['transacciones'] += 1

    db.session.commit()
    return jsonify({'success': True, 'created': created})
