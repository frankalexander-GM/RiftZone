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
    from app.services.boost_service import BOOST_PLANS
    from werkzeug.security import generate_password_hash
    SEED_USERS = [
        {'username': 'alicegamer', 'nombre': 'Alice Gamer', 'email': 'alice@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 15000, 'nivel': 42},
        {'username': 'bobstream', 'nombre': 'Bob Stream', 'email': 'bob@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 22000, 'nivel': 55},
        {'username': 'carlagames', 'nombre': 'Carla Games', 'email': 'carla@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 8900, 'nivel': 28},
        {'username': 'elenanight', 'nombre': 'Elena Night', 'email': 'elena@test.com', 'password': 'Password1', 'rol': 'jugador', 'tokens': 32000, 'nivel': 70},
        {'username': 'admin', 'nombre': 'Admin', 'email': 'admin@riftzone.com', 'password': 'admin123', 'rol': 'admin', 'tokens': 999999, 'nivel': 99},
    ]
    created = 0
    for ud in SEED_USERS:
        if not Usuario.query.filter_by(email=ud['email']).first():
            u = Usuario(username=ud['username'], nombre=ud['nombre'], email=ud['email'],
                        password=generate_password_hash(ud['password']), rol=ud['rol'],
                        tokens=ud['tokens'], nivel=ud['nivel'])
            db.session.add(u)
            created += 1
    db.session.commit()
    return jsonify({'success': True, 'created': created})
