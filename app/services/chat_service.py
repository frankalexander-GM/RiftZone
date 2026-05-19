from app.models.chat import MensajeChat
from app.models.chat_comunidad import MensajeComunidad
from app.factories.app_factory import db

class ChatService:
    def enviar_mensaje(self, usuario_id, contenido):
        if not contenido or len(contenido.strip()) == 0:
            return None
            
        mensaje = MensajeChat(
            usuario_id=usuario_id,
            contenido=contenido.strip()
        )
        
        try:
            db.session.add(mensaje)
            db.session.commit()
            return mensaje
        except Exception as e:
            db.session.rollback()
            raise e
            
    def obtener_historial(self, limite=50):
        mensajes = MensajeChat.query.order_by(MensajeChat.fecha_envio.desc()).limit(limite).all()
        return list(reversed(mensajes))

    def enviar_mensaje_comunidad(self, usuario_id, comunidad, contenido):
        if not contenido or len(contenido.strip()) == 0:
            return None
            
        mensaje = MensajeComunidad(
            usuario_id=usuario_id,
            comunidad=comunidad,
            contenido=contenido.strip()
        )
        
        try:
            db.session.add(mensaje)
            db.session.commit()
            return mensaje
        except Exception as e:
            db.session.rollback()
            raise e
            
    def obtener_historial_comunidad(self, comunidad, limite=50):
        mensajes = MensajeComunidad.query.filter_by(comunidad=comunidad).order_by(MensajeComunidad.fecha_envio.desc()).limit(limite).all()
        return list(reversed(mensajes))
