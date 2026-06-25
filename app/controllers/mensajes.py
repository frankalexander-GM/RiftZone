from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.factories.app_factory import db, socketio
from app.models.mensaje_privado import MensajePrivado, ReaccionMensaje
from app.models.usuario import Usuario
from datetime import datetime
from sqlalchemy import or_, and_
from app.utils.profanity import filter_profanity
from threading import Lock
import time

mensajes_bp = Blueprint('mensajes', __name__, template_folder='../templates/jugador')

_typing_tracker = {}
_typing_lock = Lock()


def _set_typing(usuario_id, otro_id):
    with _typing_lock:
        key = (otro_id, usuario_id)
        _typing_tracker[key] = time.time()


def _is_typing(usuario_id, otro_id):
    with _typing_lock:
        key = (usuario_id, otro_id)
        ts = _typing_tracker.get(key)
        if ts and (time.time() - ts) < 4:
            return True
        if ts:
            del _typing_tracker[key]
        return False


@mensajes_bp.route('/mensajes')
@login_required
def index():
    return render_template('mensajes.html')


@mensajes_bp.route('/mensajes/api/conversaciones')
@login_required
def conversaciones():
    user_id = current_user.id_usuario

    partner_ids = set()
    sent = db.session.query(MensajePrivado.receptor_id).filter(
        MensajePrivado.emisor_id == user_id
    ).distinct().all()
    received = db.session.query(MensajePrivado.emisor_id).filter(
        MensajePrivado.receptor_id == user_id
    ).distinct().all()
    for (rid,) in sent: partner_ids.add(rid)
    for (eid,) in received: partner_ids.add(eid)

    from app.utils.avatar import avatar_url

    resultado = []
    for pid in partner_ids:
        u = db.session.get(Usuario, pid)
        if not u:
            continue
        last_msg = MensajePrivado.query.filter(
            ((MensajePrivado.emisor_id == user_id) & (MensajePrivado.receptor_id == pid)) |
            ((MensajePrivado.receptor_id == user_id) & (MensajePrivado.emisor_id == pid))
        ).order_by(MensajePrivado.creado_en.desc()).first()
        no_leidas = MensajePrivado.query.filter(
            MensajePrivado.emisor_id == pid,
            MensajePrivado.receptor_id == user_id,
            MensajePrivado.leido == False
        ).count()
        t = last_msg.creado_en if last_msg else None
        c = last_msg.contenido if last_msg else ''
        online = u.estado == 'online'
        resultado.append({
            'usuario_id': u.id_usuario,
            'username': u.username,
            'nombre': u.nombre or u.username,
            'foto': avatar_url(u.foto_perfil),
            'ultimo_mensaje': (c[:80] + '...') if c and len(c) > 80 else c,
            'ultimo_time': t.strftime('%H:%M') if t else '',
            'ultimo_time_iso': t.isoformat() if t else '',
            'ultimo_time_completo': t.strftime('%d/%m/%Y %H:%M') if t else '',
            'no_leidas': no_leidas or 0,
            'es_premium': bool(u.es_premium),
            'online': online,
        })
    resultado.sort(key=lambda x: x['ultimo_time_iso'], reverse=True)
    return jsonify(resultado)


@mensajes_bp.route('/mensajes/api/bloquear/<int:otro_id>', methods=['POST'])
@login_required
def bloquear(otro_id):
    if otro_id == current_user.id_usuario:
        return jsonify({'success': False, 'error': 'No puedes bloquearte a ti mismo'}), 400
    from app.models.transaccion import BloqueoUsuario
    existe = BloqueoUsuario.query.filter_by(usuario_id=current_user.id_usuario, bloqueado_id=otro_id).first()
    if existe:
        db.session.delete(existe)
        db.session.commit()
        return jsonify({'success': True, 'accion': 'desbloqueado'})
    b = BloqueoUsuario(usuario_id=current_user.id_usuario, bloqueado_id=otro_id)
    db.session.add(b)
    db.session.commit()
    return jsonify({'success': True, 'accion': 'bloqueado'})


@mensajes_bp.route('/mensajes/api/bloquear/check/<int:otro_id>')
@login_required
def check_bloqueo(otro_id):
    from app.models.transaccion import BloqueoUsuario
    bloqueaste = bool(BloqueoUsuario.query.filter_by(usuario_id=current_user.id_usuario, bloqueado_id=otro_id).first())
    te_bloqueo = bool(BloqueoUsuario.query.filter_by(usuario_id=otro_id, bloqueado_id=current_user.id_usuario).first())
    return jsonify({'bloqueado': bloqueaste or te_bloqueo, 'bloqueaste': bloqueaste, 'te_bloqueo': te_bloqueo})


@mensajes_bp.route('/mensajes/api/desbloquear/<int:otro_id>', methods=['POST'])
@login_required
def desbloquear(otro_id):
    from app.models.transaccion import BloqueoUsuario
    BloqueoUsuario.query.filter_by(usuario_id=current_user.id_usuario, bloqueado_id=otro_id).delete()
    db.session.commit()
    return jsonify({'success': True})


@mensajes_bp.route('/mensajes/api/bloqueados')
@login_required
def lista_bloqueados():
    from app.models.transaccion import BloqueoUsuario
    from app.utils.avatar import avatar_url
    ids = db.session.query(BloqueoUsuario.bloqueado_id).filter(
        BloqueoUsuario.usuario_id == current_user.id_usuario
    ).all()
    ids = [r[0] for r in ids]
    usuarios = Usuario.query.filter(Usuario.id_usuario.in_(ids)).all() if ids else []
    resultado = []
    for u in usuarios:
        resultado.append({
            'usuario_id': u.id_usuario,
            'username': u.username,
            'nombre': u.nombre or u.username,
            'foto': avatar_url(u.foto_perfil),
            'es_premium': bool(u.es_premium),
        })
    return jsonify(resultado)


@mensajes_bp.route('/mensajes/api/leer/<int:otro_id>', methods=['POST'])
@login_required
def marcar_leido(otro_id):
    now = datetime.utcnow()
    MensajePrivado.query.filter_by(emisor_id=otro_id, receptor_id=current_user.id_usuario, leido=False).update(
        {'leido': True, 'leido_en': now}
    )
    db.session.commit()
    return jsonify({'success': True})


@mensajes_bp.route('/mensajes/api/eliminar/<int:otro_id>', methods=['DELETE'])
@login_required
def eliminar_conversacion(otro_id):
    user_id = current_user.id_usuario
    MensajePrivado.query.filter(
        or_(
            (MensajePrivado.emisor_id == user_id) & (MensajePrivado.receptor_id == otro_id),
            (MensajePrivado.emisor_id == otro_id) & (MensajePrivado.receptor_id == user_id)
        )
    ).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True})


@mensajes_bp.route('/mensajes/api/mensajes/<int:otro_id>')
@login_required
def obtener_mensajes(otro_id):
    user_id = current_user.id_usuario
    mensajes = MensajePrivado.query.filter(
        ((MensajePrivado.emisor_id == user_id) & (MensajePrivado.receptor_id == otro_id)) |
        ((MensajePrivado.receptor_id == user_id) & (MensajePrivado.emisor_id == otro_id))
    ).order_by(MensajePrivado.creado_en.asc()).limit(200).all()

    now = datetime.utcnow()
    MensajePrivado.query.filter(
        (MensajePrivado.emisor_id == otro_id) &
        (MensajePrivado.receptor_id == user_id) &
        (MensajePrivado.leido == False)
    ).update({'leido': True, 'leido_en': now})
    db.session.commit()

    return jsonify([m.to_dict() for m in mensajes])


@mensajes_bp.route('/mensajes/api/enviar', methods=['POST'])
@login_required
def enviar():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos inválidos'}), 400
    receptor_id = data.get('receptor_id')
    contenido = data.get('contenido', '').strip()
    imagen_url = data.get('imagen_url', '').strip() or None
    if not receptor_id or (not contenido and not imagen_url):
        return jsonify({'error': 'Faltan datos'}), 400
    if len(contenido) > 1000:
        return jsonify({'error': 'Mensaje muy largo (máx 1000 caracteres)'}), 400
    receptor = Usuario.query.get(receptor_id)
    if not receptor:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    from app.models.transaccion import BloqueoUsuario
    bloqueaste = BloqueoUsuario.query.filter_by(usuario_id=current_user.id_usuario, bloqueado_id=receptor_id).first()
    te_bloqueo = BloqueoUsuario.query.filter_by(usuario_id=receptor_id, bloqueado_id=current_user.id_usuario).first()
    if bloqueaste or te_bloqueo:
        return jsonify({'error': 'No puedes enviar mensajes a este usuario.'}), 403

    msg = MensajePrivado(
        emisor_id=current_user.id_usuario,
        receptor_id=receptor_id,
        contenido=filter_profanity(contenido),
        imagen_url=imagen_url
    )
    db.session.add(msg)
    db.session.commit()

    from app.services.notification_service import crear_notificacion
    crear_notificacion(
        usuario_id=receptor_id,
        tipo='mensaje',
        mensaje=f'Nuevo mensaje de {current_user.username}',
        enlace=f'/mensajes?chat={current_user.id_usuario}'
    )

    msg_dict = msg.to_dict()

    try:
        socketio.emit('private_message', {
            'mensaje': msg_dict,
            'de': current_user.id_usuario,
            'para': receptor_id,
        }, room=str(receptor_id))
        socketio.emit('private_message', {
            'mensaje': msg_dict,
            'de': current_user.id_usuario,
            'para': receptor_id,
        }, room=str(current_user.id_usuario))
    except:
        pass

    return jsonify(msg_dict)


@mensajes_bp.route('/mensajes/api/buscar')
@login_required
def buscar_usuarios():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    usuarios = Usuario.query.filter(
        (Usuario.username.ilike(f'%{q}%')) | (Usuario.nombre.ilike(f'%{q}%'))
    ).limit(10).all()

    from app.utils.avatar import avatar_url
    resultado = []
    for u in usuarios:
        if u.id_usuario == current_user.id_usuario:
            continue
        resultado.append({
            'usuario_id': u.id_usuario,
            'username': u.username,
            'nombre': u.nombre or u.username,
            'foto': avatar_url(u.foto_perfil),
            'es_premium': bool(u.es_premium),
        })
    return jsonify(resultado)


@mensajes_bp.route('/mensajes/api/mensajes/<int:otro_id>/buscar')
@login_required
def buscar_en_mensajes(otro_id):
    q = request.args.get('q', '').strip().lower()
    if not q or len(q) < 2:
        return jsonify([])
    user_id = current_user.id_usuario
    mensajes = MensajePrivado.query.filter(
        ((MensajePrivado.emisor_id == user_id) & (MensajePrivado.receptor_id == otro_id)) |
        ((MensajePrivado.receptor_id == user_id) & (MensajePrivado.emisor_id == otro_id))
    ).filter(MensajePrivado.contenido.ilike(f'%{q}%')
    ).order_by(MensajePrivado.creado_en.desc()).limit(30).all()
    return jsonify([m.to_dict() for m in mensajes])


@mensajes_bp.route('/mensajes/api/subir-imagen', methods=['POST'])
@login_required
def subir_imagen_mensaje():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se envió ninguna imagen'}), 400
    file = request.files['imagen']
    if not file or not file.filename:
        return jsonify({'error': 'Archivo vacío'}), 400
    from flask import current_app
    import os, uuid
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if ext not in allowed:
        return jsonify({'error': f'Formato no permitido ({ext})'}), 400
    filename = f'msg_{uuid.uuid4().hex[:12]}.{ext}'
    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'mensajes')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    url = url_for('static', filename=f'uploads/mensajes/{filename}', _external=True)
    return jsonify({'url': url})


@mensajes_bp.route('/mensajes/api/reaccionar/<int:mensaje_id>', methods=['POST'])
@login_required
def reaccionar(mensaje_id):
    data = request.get_json() or {}
    emoji = data.get('emoji', '❤️')
    msg = MensajePrivado.query.get(mensaje_id)
    if not msg:
        return jsonify({'error': 'Mensaje no encontrado'}), 404
    if msg.emisor_id != current_user.id_usuario and msg.receptor_id != current_user.id_usuario:
        return jsonify({'error': 'No tienes acceso a este mensaje'}), 403

    existing = ReaccionMensaje.query.filter_by(
        mensaje_id=mensaje_id, usuario_id=current_user.id_usuario
    ).first()

    if existing:
        if existing.emoji == emoji:
            db.session.delete(existing)
            db.session.commit()
            accion = 'removed'
        else:
            existing.emoji = emoji
            db.session.commit()
            accion = 'changed'
    else:
        r = ReaccionMensaje(mensaje_id=mensaje_id, usuario_id=current_user.id_usuario, emoji=emoji)
        db.session.add(r)
        db.session.commit()
        accion = 'added'

    return jsonify({
        'success': True,
        'accion': accion,
        'reacciones': [r.to_dict() for r in msg.reacciones.all()]
    })


@mensajes_bp.route('/mensajes/api/mensaje/<int:mensaje_id>', methods=['DELETE'])
@login_required
def eliminar_mensaje(mensaje_id):
    msg = db.session.get(MensajePrivado, mensaje_id)
    if not msg:
        return jsonify({'error': 'Mensaje no encontrado'}), 404
    if msg.emisor_id != current_user.id_usuario:
        return jsonify({'error': 'No puedes eliminar este mensaje'}), 403
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'success': True})


@mensajes_bp.route('/mensajes/api/no-leidas')
@login_required
def total_no_leidas():
    count = MensajePrivado.query.filter_by(
        receptor_id=current_user.id_usuario, leido=False
    ).count()
    return jsonify({'no_leidas': count})


@mensajes_bp.route('/mensajes/api/escribiendo', methods=['GET', 'POST'])
@login_required
def escribiendo():
    if request.method == 'POST':
        data = request.get_json() or {}
        receptor_id = data.get('receptor_id')
        if not receptor_id:
            return jsonify({'error': 'Falta receptor_id'}), 400
        _set_typing(current_user.id_usuario, receptor_id)
        return jsonify({'success': True})
    otro_id = request.args.get('otro_id', type=int)
    if not otro_id:
        return jsonify({'typing': False})
    nombre = ''
    if _is_typing(otro_id, current_user.id_usuario):
        u = db.session.get(Usuario, otro_id)
        nombre = u.username if u else ''
    return jsonify({'typing': bool(nombre), 'username': nombre})
