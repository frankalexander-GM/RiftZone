from flask import request
from flask_socketio import join_room, leave_room, emit
from app.factories.app_factory import socketio


@socketio.on('connect')
def handle_connect():
    print(f'[SocketIO] Cliente conectado desde {request.remote_addr}')


@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    if user_id:
        room = str(user_id)
        join_room(room)
        print(f'[SocketIO] Usuario {user_id} unido a sala {room}')


@socketio.on('private_message')
def handle_private_message(data):
    mensaje = data.get('mensaje')
    para = data.get('para')
    if mensaje and para:
        emit('private_message', data, room=str(para))


@socketio.on('typing')
def handle_typing(data):
    para = data.get('para')
    if para:
        data.pop('para', None)
        emit('typing', data, room=str(para))


@socketio.on('messages_read')
def handle_messages_read(data):
    otro_id = data.get('otro_id')
    leido_por = data.get('leido_por')
    if otro_id and leido_por:
        emit('messages_read', {
            'leido_por': leido_por,
            'otro_id': otro_id,
        }, room=str(otro_id))


@socketio.on('join_community')
def handle_join_community(data):
    comunidad = data.get('comunidad')
    if comunidad:
        room = 'com_' + comunidad.lower().replace(' ', '_')
        join_room(room)


@socketio.on('leave_community')
def handle_leave_community(data):
    comunidad = data.get('comunidad')
    if comunidad:
        room = 'com_' + comunidad.lower().replace(' ', '_')
        leave_room(room)


@socketio.on('community_typing')
def handle_community_typing(data):
    comunidad = data.get('comunidad')
    username = data.get('username')
    if comunidad and username:
        room = 'com_' + comunidad.lower().replace(' ', '_')
        emit('community_typing', {'username': username}, room=room, include_self=False)


@socketio.on('disconnect')
def handle_disconnect():
    print(f'[SocketIO] Cliente desconectado')
