def crear_notificacion(usuario_id, tipo, mensaje, enlace=None, icono=None):
    from app.factories.app_factory import db, socketio
    from app.models.usuario import Notificacion

    iconos = {
        'seguidor': 'fas fa-user-plus',
        'publicacion': 'fas fa-newspaper',
        'like': 'fas fa-heart',
        'comentario': 'fas fa-comment',
        'respuesta': 'fas fa-reply',
        'mencion': 'fas fa-at',
        'torneo_inscripcion': 'fas fa-trophy',
        'torneo_recordatorio': 'fas fa-clock',
        'sistema': 'fas fa-bell',
    }

    notif = Notificacion(
        usuario_id=usuario_id,
        tipo=tipo,
        mensaje=mensaje,
        enlace=enlace,
        icono=icono or iconos.get(tipo, 'fas fa-bell'),
    )
    db.session.add(notif)
    db.session.commit()

    socketio.emit('notificacion', {
        'id': notif.id_notificacion,
        'tipo': notif.tipo,
        'mensaje': notif.mensaje,
        'enlace': notif.enlace,
        'icono': notif.icono,
        'fecha': notif.fecha_creacion.isoformat() if notif.fecha_creacion else None,
    }, room=str(usuario_id))

    return notif
