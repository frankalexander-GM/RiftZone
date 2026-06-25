from app.models.usuario import Notificacion
from app.factories.app_factory import db, socketio

class NotificacionService:
    ICONOS = {
        'seguidor': 'fas fa-user-plus',
        'like': 'fas fa-heart',
        'comentario': 'fas fa-comment',
        'respuesta': 'fas fa-reply',
        'mencion': 'fas fa-at',
        'publicacion': 'fas fa-newspaper',
        'comunidad': 'fas fa-gamepad',
        'sistema': 'fas fa-bell',
    }

    def crear_notificacion(self, usuario_id, tipo, mensaje, enlace=None, icono=None):
        notificacion = Notificacion(
            usuario_id=usuario_id,
            tipo=tipo,
            mensaje=mensaje,
            enlace=enlace,
            icono=icono or self.ICONOS.get(tipo, 'fas fa-bell'),
        )
        db.session.add(notificacion)
        db.session.flush()

        try:
            socketio.emit('notificacion', {
                'id': notificacion.id_notificacion,
                'tipo': tipo,
                'mensaje': mensaje,
                'enlace': enlace,
                'icono': icono or self.ICONOS.get(tipo, 'fas fa-bell'),
                'fecha': notificacion.fecha_creacion.isoformat() if notificacion.fecha_creacion else None,
            }, room=str(usuario_id))
        except:
            pass

        limite = 10
        total = Notificacion.query.filter_by(usuario_id=usuario_id).count()
        if total > limite:
            exceso = total - limite
            viejas = Notificacion.query.filter_by(usuario_id=usuario_id).order_by(Notificacion.fecha_creacion.asc()).limit(exceso).all()
            for v in viejas:
                db.session.delete(v)

        db.session.commit()
        return notificacion

    def obtener_notificaciones(self, usuario_id, limite=20):
        return Notificacion.query.filter_by(usuario_id=usuario_id).order_by(Notificacion.fecha_creacion.desc()).limit(limite).all()

    def no_leidas_count(self, usuario_id):
        return Notificacion.query.filter_by(usuario_id=usuario_id, leido=False).count()

    def marcar_leidas(self, usuario_id):
        Notificacion.query.filter_by(usuario_id=usuario_id, leido=False).update({'leido': True})
        db.session.commit()
