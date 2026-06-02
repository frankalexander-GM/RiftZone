from flask import request
from app.factories.app_factory import socketio

@socketio.on('connect')
def handle_connect():
    print(f'[SocketIO] Cliente conectado desde {request.remote_addr}')

@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    if user_id:
        room = str(user_id)
        socketio.join_room(room)
        print(f'[SocketIO] Usuario {user_id} unido a sala {room}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'[SocketIO] Cliente desconectado')
