"""Utilidades de membresía VIP."""

PLANES_VIP = {
    'plata': {
        'nombre': 'Pase Plata',
        'monedas': 500,
        'titulo': 'VIP Plata',
        'marco': 'border: 2px solid #C0C0C0; box-shadow: 0 0 8px #C0C0C0;',
    },
    'oro': {
        'nombre': 'Pase Oro',
        'monedas': 1500,
        'titulo': 'VIP Oro',
        'marco': 'border: 2px solid #FACC15; box-shadow: 0 0 10px #FACC15;',
    },
    'diamante': {
        'nombre': 'Pase Diamante',
        'monedas': 4000,
        'titulo': 'VIP Diamante',
        'marco': 'border: 3px solid #00E5FF; box-shadow: 0 0 15px #00E5FF;',
    },
}

ORDEN_PLANES = ('plata', 'oro', 'diamante')


def descripcion_bono_plan(nombre_plan):
    return f'Bono por Suscripción: {nombre_plan}'


def plan_ya_reclamado(user_id, plan_key):
    """True si el usuario ya activó este pase (una sola vez por plan)."""
    from app.models.transaccion import Transaccion

    plan = PLANES_VIP.get(plan_key)
    if not plan:
        return True
    desc = descripcion_bono_plan(plan['nombre'])
    if Transaccion.query.filter_by(user_id=user_id, description=desc).first():
        return True
    # Compatibilidad con registros antiguos del mismo pase
    return (
        Transaccion.query.filter(
            Transaccion.user_id == user_id,
            Transaccion.description.contains(plan['nombre']),
            Transaccion.tipo == 'ingreso',
        ).first()
        is not None
    )


def planes_reclamados(user_id):
    """Lista de claves de planes ya activados: ['plata', 'oro', ...]."""
    return [p for p in ORDEN_PLANES if plan_ya_reclamado(user_id, p)]


def aplicar_plan_vip(user, plan_key):
    """
    Activa un pase VIP si no fue reclamado antes.
    Retorna (plan_info, monedas) o lanza ValueError.
    """
    from app.factories.app_factory import db
    from app.models.transaccion import Transaccion

    plan = PLANES_VIP.get(plan_key)
    if not plan:
        raise ValueError('Plan de membresía no válido.')

    if plan_ya_reclamado(user.id_usuario, plan_key):
        raise ValueError(f'Ya activaste el {plan["nombre"]}. Solo se puede reclamar una vez.')

    user.es_premium = True
    user.membresia_tipo = plan_key
    user.tokens = (user.tokens or 0) + plan['monedas']
    user.titulo_perfil = plan['titulo']
    user.marco_perfil = plan['marco']

    tx = Transaccion(
        user_id=user.id_usuario,
        amount=plan['monedas'],
        tipo='ingreso',
        description=descripcion_bono_plan(plan['nombre']),
    )
    db.session.add(tx)
    db.session.commit()
    return plan, plan['monedas']


def strip_vip(user):
    """Quita estatus VIP, marco y título de membresía del usuario."""
    if not user:
        return
    user.es_premium = False
    user.membresia_tipo = 'ninguna'
    titulo = (user.titulo_perfil or '').strip()
    if titulo.upper().startswith('VIP'):
        user.titulo_perfil = 'Gamer'
    marco = user.marco_perfil or ''
    if any(x in marco for x in ('FACC15', 'C0C0C0', '00E5FF', '#C0C0C0')):
        user.marco_perfil = None
