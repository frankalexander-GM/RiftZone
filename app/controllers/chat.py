from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.factories.service_factory import get_service_factory

chat_bp = Blueprint('chat', __name__, template_folder='../templates/chat')

@chat_bp.route('/global')
@login_required
def chat_global():
    return render_template('jugador/chat_global.html')

@chat_bp.route('/api/mensajes', methods=['GET'])
@login_required
def obtener_mensajes():
    sf = get_service_factory()
    chat_service = sf.get_chat_service()
    mensajes = chat_service.obtener_historial()
    
    return jsonify({
        'mensajes': [msg.to_dict() for msg in mensajes]
    })

@chat_bp.route('/api/enviar', methods=['POST'])
@login_required
def enviar_mensaje():
    data = request.json
    contenido = data.get('contenido')
    
    if not contenido:
        return jsonify({'error': 'Mensaje vacío'}), 400
        
    sf = get_service_factory()
    chat_service = sf.get_chat_service()
    
    mensaje = chat_service.enviar_mensaje(current_user.id_usuario, contenido)
    
    if mensaje:
        return jsonify({'status': 'success', 'mensaje': mensaje.to_dict()})
    
    return jsonify({'error': 'Error al enviar'}), 500

@chat_bp.route('/sala/<comunidad>')
@login_required
def chat_sala(comunidad):
    return render_template('jugador/chat_comunidad.html', comunidad=comunidad)

@chat_bp.route('/api/mensajes/<comunidad>', methods=['GET'])
@login_required
def obtener_mensajes_comunidad(comunidad):
    sf = get_service_factory()
    chat_service = sf.get_chat_service()
    mensajes = chat_service.obtener_historial_comunidad(comunidad)
    
    return jsonify({
        'mensajes': [msg.to_dict() for msg in mensajes]
    })

@chat_bp.route('/api/enviar/<comunidad>', methods=['POST'])
@login_required
def enviar_mensaje_comunidad(comunidad):
    data = request.json
    contenido = data.get('contenido')
    
    if not contenido:
        return jsonify({'error': 'Mensaje vacío'}), 400
        
    sf = get_service_factory()
    chat_service = sf.get_chat_service()
    
    mensaje = chat_service.enviar_mensaje_comunidad(current_user.id_usuario, comunidad, contenido)
    
    if mensaje:
        return jsonify({'status': 'success', 'mensaje': mensaje.to_dict()})
    
    return jsonify({'error': 'Error al enviar'}), 500
