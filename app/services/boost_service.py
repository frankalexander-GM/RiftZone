from datetime import datetime, timedelta

from app.factories.app_factory import db
from app.models.publicacion import Publicacion
from app.models.transaccion import Transaccion
from app.models.usuario import Notificacion

BOOST_PLANS = {
    'rapido': {
        'nombre': 'Boost Rápido',
        'costo': 100,
        'horas': 24,
        'notify_followers': False,
        'color': '#3B82F6',
        'color_rgb': '59, 130, 246',
        'icon': 'fa-fighter-jet',
        'etiqueta': 'RÁPIDO',
    },
    'mega': {
        'nombre': 'Mega Boost',
        'costo': 250,
        'horas': 72,
        'notify_followers': False,
        'color': '#A855F7',
        'color_rgb': '168, 85, 247',
        'icon': 'fa-space-shuttle',
        'etiqueta': 'MEGA',
    },
    'titan': {
        'nombre': 'Boost Titán',
        'costo': 600,
        'horas': 168,
        'notify_followers': True,
        'color': '#FACC15',
        'color_rgb': '250, 204, 21',
        'icon': 'fa-crown',
        'etiqueta': 'TITÁN',
    },
}


def tema_boost(plan_key):
    """Colores e iconos del plan para plantillas."""
    plan = BOOST_PLANS.get(plan_key, BOOST_PLANS['mega'])
    return {
        'key': plan_key,
        'color': plan['color'],
        'color_rgb': plan['color_rgb'],
        'icon': plan['icon'],
        'etiqueta': plan['etiqueta'],
        'nombre': plan['nombre'],
    }


def boost_activo_usuario(user_id):
    """Plan de boost vigente del usuario (el de mayor nivel si tiene varios)."""
    if not user_id:
        return None
    limpiar_boosts_expirados()
    now = datetime.utcnow()
    posts = Publicacion.query.filter(
        Publicacion.id_usuario == user_id,
        Publicacion.promocionada.is_(True),
        Publicacion.boost_hasta.isnot(None),
        Publicacion.boost_hasta > now,
        Publicacion.boost_tipo.isnot(None),
    ).all()
    rank = {'rapido': 1, 'mega': 2, 'titan': 3}
    best = None
    best_rank = 0
    for post in posts:
        r = rank.get(post.boost_tipo, 0)
        if r > best_rank:
            best_rank = r
            best = post.boost_tipo
    return best


def color_nombre_boost(user_id):
    """Color hex del nombre cuando hay boost activo."""
    plan_key = boost_activo_usuario(user_id)
    if not plan_key:
        return None
    return tema_boost(plan_key)['color']


def limpiar_boosts_expirados():
    """Desactiva publicaciones cuyo boost ya venció."""
    now = datetime.utcnow()
    expiradas = Publicacion.query.filter(
        Publicacion.boost_hasta.isnot(None),
        Publicacion.boost_hasta < now,
    ).all()
    for post in expiradas:
        post.promocionada = False
        post.boost_tipo = None
        post.boost_hasta = None
    if expiradas:
        db.session.commit()


def aplicar_boost(usuario, post_id, plan_key):
    plan = BOOST_PLANS.get(plan_key)
    if not plan:
        raise ValueError('Plan de boost no válido.')

    post = Publicacion.query.get(post_id)
    if not post:
        raise ValueError('Publicación no encontrada.')
    if post.id_usuario != usuario.id_usuario:
        raise ValueError('Solo puedes boostear tus propias publicaciones.')

    limpiar_boosts_expirados()

    costo = plan['costo']
    if (usuario.tokens or 0) < costo:
        raise ValueError(f'Necesitas {costo} RiftCoins. Tu saldo: {usuario.tokens or 0} RC.')

    ahora = datetime.utcnow()
    post.promocionada = True
    post.boost_tipo = plan_key
    post.boost_hasta = ahora + timedelta(hours=plan['horas'])

    usuario.tokens -= costo
    tx = Transaccion(
        user_id=usuario.id_usuario,
        amount=-costo,
        type='egreso',
        description=f"{plan['nombre']} — publicación #{post.id_publicacion}",
    )
    db.session.add(tx)

    if plan.get('notify_followers'):
        for seguidor in usuario.seguidores_list.all():
            notif = Notificacion(
                usuario_id=seguidor.id_usuario,
                mensaje=f'{usuario.nombre or usuario.username} destacó una publicación con Boost Titán.',
                icono='fas fa-rocket',
                enlace=url_for_dashboard_post(post.id_publicacion),
                tipo='boost',
            )
            db.session.add(notif)

    db.session.commit()
    return post, plan


def url_for_dashboard_post(post_id):
    return f'/jugador/dashboard#post-{post_id}'
