from app.models.clan import Clan, MiembroClan
from app.factories.app_factory import db

class ClanService:
    def crear_clan(self, lider_id, nombre, descripcion, logo_url=None, banner_url=None, privacidad='publico'):
        if not nombre or len(nombre.strip()) < 3:
            raise ValueError("El nombre del clan debe tener al menos 3 caracteres.")
            
        # Verificar si el usuario ya está en 5 clanes
        clanes_actuales = MiembroClan.query.filter_by(usuario_id=lider_id).count()
        if clanes_actuales >= 5:
            raise ValueError("Has alcanzado el límite máximo de 5 clanes. Debes salir de uno para crear otro nuevo.")
            
        nuevo_clan = Clan(
            lider_id=lider_id,
            nombre=nombre.strip(),
            descripcion=descripcion.strip() if descripcion else "",
            logo_url=logo_url.strip() if logo_url else "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=200&auto=format&fit=crop",
            banner_url=banner_url.strip() if banner_url else "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=1200&auto=format&fit=crop",
            privacidad=privacidad
        )
        
        try:
            db.session.add(nuevo_clan)
            db.session.flush() # Guarda temporalmente para generar el ID del clan
            
            # Asignar automáticamente al creador como Líder
            miembro_lider = MiembroClan(
                clan_id=nuevo_clan.id_clan,
                usuario_id=lider_id,
                rol='lider'
            )
            db.session.add(miembro_lider)
            db.session.commit()
            
            return nuevo_clan
        except Exception as e:
            db.session.rollback()
            if "UNIQUE" in str(e).upper() or "UNIQUE constraint failed" in str(e):
                raise ValueError("Ese nombre de clan ya está en uso. ¡Elige uno diferente!")
            raise ValueError(f"Error interno al crear el clan: {str(e)}")
            
    def unirse_clan(self, clan_id, usuario_id):
        # Verificar si el usuario ya está en 5 clanes
        clanes_actuales = MiembroClan.query.filter_by(usuario_id=usuario_id).count()
        if clanes_actuales >= 5:
            raise ValueError("Has alcanzado el límite máximo de 5 clanes. Debes abandonar uno para unirte a este.")
            
        clan = Clan.query.get(clan_id)
        if not clan:
            raise ValueError("El clan no existe.")
            
        # Verificar si ya solicitó
        from app.models.clan import SolicitudClan
        ya_solicito = SolicitudClan.query.filter_by(clan_id=clan_id, usuario_id=usuario_id, estado='pendiente').first()
        if ya_solicito:
            raise ValueError("Ya has enviado una solicitud a este clan. Espera a que el líder la revise.")
            
        if clan.privacidad == 'privado':
            nueva_solicitud = SolicitudClan(clan_id=clan_id, usuario_id=usuario_id)
            db.session.add(nueva_solicitud)
            db.session.commit()
            return clan, "solicitud"
        else:
            nuevo_miembro = MiembroClan(
                clan_id=clan_id,
                usuario_id=usuario_id,
                rol='miembro'
            )
            db.session.add(nuevo_miembro)
            db.session.commit()
            return clan, "unido"
            
    def gestionar_solicitud(self, solicitud_id, lider_id, accion):
        from app.models.clan import SolicitudClan
        solicitud = SolicitudClan.query.get(solicitud_id)
        if not solicitud:
            raise ValueError("La solicitud no existe.")
            
        clan = Clan.query.get(solicitud.clan_id)
        miembro_lider = MiembroClan.query.filter_by(clan_id=clan.id_clan, usuario_id=lider_id).first()
        if not miembro_lider or miembro_lider.rol not in ['lider', 'moderador']:
            raise ValueError("No tienes permisos para gestionar solicitudes en este clan.")
            
        if accion == 'aceptar':
            # Verificar si el usuario ya superó el límite mientras esperaba
            clanes_actuales = MiembroClan.query.filter_by(usuario_id=solicitud.usuario_id).count()
            if clanes_actuales >= 5:
                solicitud.estado = 'rechazada'
                db.session.commit()
                raise ValueError("El usuario alcanzó su límite de clanes y su solicitud fue cancelada.")
                
            nuevo_miembro = MiembroClan(clan_id=clan.id_clan, usuario_id=solicitud.usuario_id, rol='miembro')
            db.session.add(nuevo_miembro)
            solicitud.estado = 'aceptada'
            
            # Notificar al usuario
            from app.models.usuario import Notificacion
            notif = Notificacion(usuario_id=solicitud.usuario_id, mensaje=f'¡Felicidades! Has sido aceptado en el clan {clan.nombre}.')
            db.session.add(notif)
            
        elif accion == 'rechazar':
            solicitud.estado = 'rechazada'
            
            # Notificar al usuario
            from app.models.usuario import Notificacion
            notif = Notificacion(usuario_id=solicitud.usuario_id, mensaje=f'El líder del clan {clan.nombre} ha rechazado tu solicitud.')
            db.session.add(notif)
            
        db.session.commit()
        return solicitud
        
    def abandonar_clan(self, clan_id, usuario_id):
        from app.models.clan import MiembroClan
        miembro = MiembroClan.query.filter_by(clan_id=clan_id, usuario_id=usuario_id).first()
        if not miembro:
            raise ValueError("No eres miembro de este clan.")
            
        if miembro.rol == 'lider':
            raise ValueError("El líder fundador no puede abandonar el clan, debe disolverlo.")
            
        db.session.delete(miembro)
        db.session.commit()
        return True
        
    def editar_clan(self, clan_id, lider_id, nombre, descripcion, logo_url, banner_url, privacidad):
        clan = Clan.query.get(clan_id)
        if not clan:
            raise ValueError("El clan no existe")
            
        miembro = MiembroClan.query.filter_by(clan_id=clan_id, usuario_id=lider_id).first()
        if not miembro or miembro.rol not in ['lider', 'administrador']:
            raise ValueError("No tienes permisos para editar el clan.")
            
        if clan.nombre != nombre.strip():
            existe = Clan.query.filter_by(nombre=nombre.strip()).first()
            if existe:
                raise ValueError("El nombre ya está en uso.")
                
        clan.nombre = nombre.strip()
        clan.descripcion = descripcion.strip()
        if logo_url: clan.logo_url = logo_url.strip()
        if banner_url: clan.banner_url = banner_url.strip()
        if privacidad: clan.privacidad = privacidad
        db.session.commit()
        return clan
        
    def expulsar_miembro(self, clan_id, lider_id, usuario_expulsar_id):
        miembro_ejecutor = MiembroClan.query.filter_by(clan_id=clan_id, usuario_id=lider_id).first()
        if not miembro_ejecutor or miembro_ejecutor.rol not in ['lider', 'administrador']:
            raise ValueError("No tienes permisos para expulsar miembros.")
            
        miembro_objetivo = MiembroClan.query.filter_by(clan_id=clan_id, usuario_id=usuario_expulsar_id).first()
        if not miembro_objetivo:
            raise ValueError("El usuario no es miembro del clan.")
            
        if miembro_objetivo.rol == 'lider':
            raise ValueError("No puedes expulsar al líder.")
            
        db.session.delete(miembro_objetivo)
        db.session.commit()
        return True
        
    def transferir_liderazgo(self, clan_id, lider_actual_id, nuevo_lider_id):
        from app.models.clan import Clan, MiembroClan
        miembro_lider = MiembroClan.query.filter_by(clan_id=clan_id, usuario_id=lider_actual_id).first()
        if not miembro_lider or miembro_lider.rol != 'lider':
            raise ValueError("Solo el líder actual puede transferir el mando.")
            
        nuevo_lider = MiembroClan.query.filter_by(clan_id=clan_id, usuario_id=nuevo_lider_id).first()
        if not nuevo_lider:
            raise ValueError("El usuario objetivo no es miembro del clan.")
            
        # Intercambiar roles
        miembro_lider.rol = 'administrador'
        nuevo_lider.rol = 'lider'
        
        clan = Clan.query.get(clan_id)
        clan.lider_id = nuevo_lider_id
        
        db.session.commit()
        return True
        
    def obtener_clanes(self):
        return Clan.query.order_by(Clan.fecha_creacion.desc()).all()
