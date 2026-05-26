from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.factories.service_factory import get_service_factory

chat_bp = Blueprint('chat', __name__, template_folder='../templates/chat')


def _json_body():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict()


@chat_bp.route('/global')
@login_required
def chat_global():
    return render_template('jugador/chat_global.html')

@chat_bp.route('/api/mensajes', methods=['GET'])
@login_required
def obtener_mensajes():
    try:
        sf = get_service_factory()
        chat_service = sf.get_chat_service()
        mensajes = chat_service.obtener_historial()
        return jsonify({
            'success': True,
            'mensajes': [msg.to_dict() for msg in mensajes],
        })
    except Exception as e:
        current_app.logger.exception('Error cargando chat mundial: %s', e)
        return jsonify({
            'success': False,
            'mensajes': [],
            'error': 'No se pudo cargar el chat. Reinicia el servidor.',
        }), 500

@chat_bp.route('/api/enviar', methods=['POST'])
@login_required
def enviar_mensaje():
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'error': 'Regístrate para escribir en el chat.'}), 403

    data = _json_body()
    contenido = (data.get('contenido') or '').strip()

    if not contenido:
        return jsonify({'success': False, 'error': 'Mensaje vacío'}), 400

    try:
        sf = get_service_factory()
        chat_service = sf.get_chat_service()
        mensaje = chat_service.enviar_mensaje(current_user.id_usuario, contenido)
        if mensaje:
            return jsonify({'success': True, 'mensaje': mensaje.to_dict()})
        return jsonify({'success': False, 'error': 'Error al enviar'}), 500
    except Exception as e:
        current_app.logger.exception('Error enviando mensaje chat: %s', e)
        return jsonify({'success': False, 'error': 'No se pudo enviar el mensaje.'}), 500

@chat_bp.route('/sala/<comunidad>')
@login_required
def chat_sala(comunidad):
    return render_template('jugador/chat_comunidad.html', comunidad=comunidad)

@chat_bp.route('/api/mensajes/<comunidad>', methods=['GET'])
@login_required
def obtener_mensajes_comunidad(comunidad):
    try:
        sf = get_service_factory()
        chat_service = sf.get_chat_service()
        mensajes = chat_service.obtener_historial_comunidad(comunidad)
        return jsonify({
            'success': True,
            'mensajes': [msg.to_dict() for msg in mensajes],
        })
    except Exception as e:
        current_app.logger.exception('Error chat comunidad %s: %s', comunidad, e)
        return jsonify({'success': False, 'mensajes': [], 'error': 'No se pudo cargar el chat.'}), 500

@chat_bp.route('/api/enviar/<comunidad>', methods=['POST'])
@login_required
def enviar_mensaje_comunidad(comunidad):
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'error': 'Regístrate para escribir.'}), 403

    data = _json_body()
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
            return jsonify({'success': True, 'mensaje': mensaje.to_dict()})
        return jsonify({'success': False, 'error': 'Error al enviar'}), 500
    except Exception as e:
        current_app.logger.exception('Error enviando chat comunidad: %s', e)
        return jsonify({'success': False, 'error': 'No se pudo enviar.'}), 500
