from flask import Blueprint, render_template, request, jsonify, current_app, make_response
from flask_login import login_required, current_user
from app.factories.app_factory import db, socketio
from app.factories.service_factory import get_service_factory

chat_bp = Blueprint('chat', __name__, template_folder='../templates/chat')

ROOMS_META = {
    'general':  {'label': 'General',      'icon': 'hashtag',         'desc': 'Habla con toda la comunidad'},
}
VALID_ROOMS = set(ROOMS_META.keys())


def _json_body():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict()


@chat_bp.route('/global')
@login_required
def chat_global():
    return render_template('jugador/chat_global.html')


# ─── API: listar salas ────────────────────────────────────────────────────────
@chat_bp.route('/api/total-msgs', methods=['GET'])
@login_required
def total_mensajes():
    try:
        from app.models.chat import MensajeChat
        total = MensajeChat.query.count()
        vistos = current_user.chat_ultimo_visto or 0
        no_leidos = max(0, total - vistos)
        return jsonify({'total': total, 'no_leidos': no_leidos})
    except Exception as e:
        return jsonify({'total': 0, 'no_leidos': 0})


@chat_bp.route('/api/marcar-visto', methods=['POST'])
@login_required
def marcar_visto():
    try:
        from app.models.chat import MensajeChat
        total = MensajeChat.query.count()
        current_user.chat_ultimo_visto = total
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False}), 500


@chat_bp.route('/api/salas', methods=['GET'])
@login_required
def api_salas():
    return jsonify({'success': True, 'salas': ROOMS_META})


# ─── API: obtener mensajes (global + por sala) ────────────────────────────────
@chat_bp.route('/api/mensajes', methods=['GET'])
@login_required
def obtener_mensajes():
    room  = request.args.get('room', 'general').strip().lower()
    limit = min(int(request.args.get('limit', 60)), 100)

    try:
        sf = get_service_factory()
        chat_service = sf.get_chat_service()

        if room == 'general':
            mensajes = chat_service.obtener_historial(limite=limit)
        else:
            if room not in VALID_ROOMS:
                room = 'general'
                mensajes = chat_service.obtener_historial(limite=limit)
            else:
                mensajes = chat_service.obtener_historial_comunidad(room, limite=limit)

        return jsonify({
            'success': True,
            'room': room,
            'mensajes': [msg.to_dict() for msg in mensajes],
        })
    except Exception as e:
        current_app.logger.exception('Error cargando chat: %s', e)
        return jsonify({'success': False, 'mensajes': [], 'error': 'No se pudo cargar el chat.'}), 500


# ─── API: enviar mensaje ──────────────────────────────────────────────────────
@chat_bp.route('/api/enviar', methods=['POST'])
@login_required
def enviar_mensaje():
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'error': 'Regístrate para escribir en el chat.'}), 403

    data     = _json_body()
    contenido = (data.get('contenido') or '').strip()
    room      = (data.get('room') or 'general').strip().lower()

    if not contenido:
        return jsonify({'success': False, 'error': 'Mensaje vacío'}), 400
    if len(contenido) > 500:
        return jsonify({'success': False, 'error': 'Mensaje demasiado largo (máx. 500 caracteres)'}), 400

    try:
        sf = get_service_factory()
        chat_service = sf.get_chat_service()

        if room == 'general':
            mensaje = chat_service.enviar_mensaje(current_user.id_usuario, contenido)
        else:
            if room not in VALID_ROOMS:
                room = 'general'
                mensaje = chat_service.enviar_mensaje(current_user.id_usuario, contenido)
            else:
                mensaje = chat_service.enviar_mensaje_comunidad(
                    current_user.id_usuario, room, contenido
                )

        if mensaje:
            try:
                from app.models.chat import MensajeChat
                total = MensajeChat.query.count()
                socketio.emit('chat_message', {'total': total}, broadcast=True)
            except:
                pass
            return jsonify({'success': True, 'mensaje': mensaje.to_dict(), 'room': room})
        return jsonify({'success': False, 'error': 'Error al enviar'}), 500
    except Exception as e:
        current_app.logger.exception('Error enviando mensaje chat: %s', e)
        return jsonify({'success': False, 'error': 'No se pudo enviar el mensaje.'}), 500


# ─── Sala de comunidad (ruta legacy) ─────────────────────────────────────────
@chat_bp.route('/sala/<comunidad>')
@login_required
def chat_sala(comunidad):
    from app.data.game_categories import get_game_categories
    color = '#8b5cf6'
    for cat in get_game_categories():
        for g in cat['juegos']:
            if g['nombre'].lower() == comunidad.lower():
                color = cat['color']
                break
        else:
            continue
        break
    siguiendo = current_user.esta_siguiendo_comunidad(comunidad)
    resp = make_response(render_template('jugador/chat_comunidad.html', comunidad=comunidad, color=color, siguiendo=siguiendo))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@chat_bp.route('/api/mensajes/<comunidad>', methods=['GET'])
@login_required
def obtener_mensajes_comunidad(comunidad):
    try:
        sf = get_service_factory()
        chat_service = sf.get_chat_service()
        mensajes = chat_service.obtener_historial_comunidad(comunidad)
        return jsonify({'success': True, 'mensajes': [msg.to_dict() for msg in mensajes]})
    except Exception as e:
        current_app.logger.exception('Error chat comunidad %s: %s', comunidad, e)
        return jsonify({'success': False, 'mensajes': [], 'error': 'No se pudo cargar el chat.'}), 500


@chat_bp.route('/api/enviar/<comunidad>', methods=['POST'])
@login_required
def enviar_mensaje_comunidad(comunidad):
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'error': 'Regístrate para escribir.'}), 403

    data      = _json_body()
    contenido = (data.get('contenido') or '').strip()

    if not contenido:
        return jsonify({'success': False, 'error': 'Mensaje vacío'}), 400

    try:
        sf = get_service_factory()
        chat_service = sf.get_chat_service()
        mensaje = chat_service.enviar_mensaje_comunidad(
            current_user.id_usuario, comunidad, contenido
        )
        if mensaje:
            try:
                room = 'com_' + comunidad.lower().replace(' ', '_')
                socketio.emit('community_message', {
                    'mensaje': mensaje.to_dict(),
                    'comunidad': comunidad
                }, room=room)
            except:
                pass
            return jsonify({'success': True, 'mensaje': mensaje.to_dict()})
        return jsonify({'success': False, 'error': 'Error al enviar'}), 500
    except Exception as e:
        current_app.logger.exception('Error enviando chat comunidad: %s', e)
        return jsonify({'success': False, 'error': 'No se pudo enviar.'}), 500


@chat_bp.route('/api/reaccionar/<int:mensaje_id>', methods=['POST'])
@login_required
def reaccionar_mensaje_comunidad(mensaje_id):
    from app.models.chat_comunidad import MensajeComunidad, ReaccionMensajeComunidad
    data = request.get_json() or {}
    emoji = data.get('emoji', '❤️')
    msg = MensajeComunidad.query.get(mensaje_id)
    if not msg:
        return jsonify({'error': 'Mensaje no encontrado'}), 404

    existing = ReaccionMensajeComunidad.query.filter_by(
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
        r = ReaccionMensajeComunidad(mensaje_id=mensaje_id, usuario_id=current_user.id_usuario, emoji=emoji)
        db.session.add(r)
        db.session.commit()
        accion = 'added'

    reacciones = [r.to_dict() for r in msg.reacciones.all()]

    try:
        room = 'com_' + msg.comunidad.lower().replace(' ', '_')
        socketio.emit('community_reaction', {
            'mensaje_id': mensaje_id,
            'reacciones': reacciones,
            'comunidad': msg.comunidad
        }, room=room)
    except:
        pass

    return jsonify({
        'success': True,
        'accion': accion,
        'reacciones': reacciones
    })


@chat_bp.route('/api/mensaje/<int:mensaje_id>', methods=['DELETE'])
@login_required
def eliminar_mensaje_comunidad(mensaje_id):
    from app.models.chat_comunidad import MensajeComunidad
    msg = MensajeComunidad.query.get(mensaje_id)
    if not msg:
        return jsonify({'error': 'Mensaje no encontrado'}), 404
    if msg.usuario_id != current_user.id_usuario:
        return jsonify({'error': 'No puedes eliminar este mensaje'}), 403

    comunidad = msg.comunidad
    db.session.delete(msg)
    db.session.commit()

    try:
        room = 'com_' + comunidad.lower().replace(' ', '_')
        socketio.emit('community_message_delete', {
            'mensaje_id': mensaje_id,
            'comunidad': comunidad
        }, room=room)
    except:
        pass

    return jsonify({'success': True})
