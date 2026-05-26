from app.models.usuario import Notificacion
from app.factories.app_factory import db

class NotificacionService:
    def crear_notificacion(self, usuario_id, tipo, mensaje, enlace=None):
        notificacion = Notificacion(
            usuario_id=usuario_id,
            mensaje=mensaje,
            tipo=tipo,
            enlace=enlace,
        )
        db.session.add(notificacion)
        return notificacion
