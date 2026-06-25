from datetime import date, datetime, timedelta

MISIONES_DIARIAS = [
    {
        'id': 'publicar',
        'nombre': 'Comparte algo con la comunidad',
        'descripcion': 'Crea una publicación en el feed',
        'icono': 'fas fa-pen-fancy',
        'tokens': 30,
        'requisito': 1,
    },
    {
        'id': 'likes',
        'nombre': 'Esparce amor',
        'descripcion': 'Dale like a publicaciones',
        'icono': 'fas fa-heart',
        'tokens': 20,
        'requisito': 3,
    },
    {
        'id': 'comentar',
        'nombre': 'Opina y participa',
        'descripcion': 'Comenta en publicaciones',
        'icono': 'fas fa-comment',
        'tokens': 25,
        'requisito': 2,
    },
    {
        'id': 'popular',
        'nombre': 'Estrella del feed',
        'descripcion': 'Recibe likes en tus publicaciones',
        'icono': 'fas fa-star',
        'tokens': 35,
        'requisito': 5,
    },
    {
        'id': 'chat',
        'nombre': 'Conversa en el chat',
        'descripcion': 'Envía mensajes en el chat global',
        'icono': 'fas fa-comment-dots',
        'tokens': 20,
        'requisito': 5,
    },
    {
        'id': 'compartir',
        'nombre': 'Comparte contenido',
        'descripcion': 'Comparte publicaciones de otros',
        'icono': 'fas fa-share-alt',
        'tokens': 25,
        'requisito': 2,
    },
    {
        'id': 'megusta',
        'nombre': 'Rey de los likes',
        'descripcion': 'Acumula likes en tus publicaciones',
        'icono': 'fas fa-crown',
        'tokens': 50,
        'requisito': 10,
    },
]

RECOMPENSA_BASE = 50
BONUS_STREAK_POR_DIA = 5
STREAK_HITOS = {7: 100, 14: 250, 30: 500}

def calcular_recompensa_diaria(usuario):
    racha = usuario.racha_dias or 0
    monto = RECOMPENSA_BASE + (racha * BONUS_STREAK_POR_DIA)
    for dias, bonus in sorted(STREAK_HITOS.items(), reverse=True):
        if racha >= dias:
            monto += bonus
            break
    return monto

def procesar_recompensa_diaria(usuario):
    from app.factories.app_factory import db
    from app.models.transaccion import Transaccion

    hoy = date.today()
    ayer = hoy - timedelta(days=1)

    if usuario.ultima_recompensa_diaria == hoy:
        return {'success': False, 'message': 'Ya reclamaste hoy.'}

    if usuario.ultima_recompensa_diaria == ayer:
        usuario.racha_dias = (usuario.racha_dias or 0) + 1
    else:
        usuario.racha_dias = 1

    monto = calcular_recompensa_diaria(usuario)
    usuario.tokens = (usuario.tokens or 0) + monto
    usuario.ultima_recompensa_diaria = hoy

    tx = Transaccion(
        user_id=usuario.id_usuario,
        amount=monto,
        tipo='ingreso',
        description=f'Recompensa diaria (racha: {usuario.racha_dias} día{"s" if usuario.racha_dias != 1 else ""})',
    )
    db.session.add(tx)

    hitos_alcanzados = []
    for dias, bonus in STREAK_HITOS.items():
        if usuario.racha_dias == dias:
            usuario.tokens = (usuario.tokens or 0) + bonus
            hitos_alcanzados.append(dias)

    db.session.commit()
    return {
        'success': True,
        'monto': monto,
        'racha': usuario.racha_dias,
        'hitos': hitos_alcanzados,
    }

def _reclamadas_hoy(usuario):
    hoy = date.today()
    if usuario.ultimo_dia_misiones != hoy:
        usuario.ultimo_dia_misiones = hoy
        usuario.misiones_reclamadas_hoy = ''
        return set()
    raw = (usuario.misiones_reclamadas_hoy or '').strip()
    return set(raw.split(',')) if raw else set()

def verificar_misiones(usuario):
    from app.factories.app_factory import db
    from app.models.publicacion import Publicacion, publicacion_likes
    from app.models.comentario import Comentario

    hoy = date.today()
    inicio_hoy = datetime.combine(hoy, datetime.min.time())
    reclamadas = _reclamadas_hoy(usuario)

    misiones_completadas = []
    misiones_progreso = []

    pub_count = Publicacion.query.filter(
        Publicacion.id_usuario == usuario.id_usuario,
        Publicacion.fecha_creacion >= inicio_hoy,
    ).count()
    completada = pub_count >= 1
    misiones_progreso.append({
        'id': 'publicar',
        'actual': min(pub_count, 1),
        'requisito': 1,
        'completada': completada,
        'reclamada': 'publicar' in reclamadas,
    })
    if completada:
        misiones_completadas.append('publicar')

    likes_count = db.session.query(publicacion_likes).join(
        Publicacion, publicacion_likes.c.id_publicacion == Publicacion.id_publicacion
    ).filter(
        Publicacion.id_usuario != usuario.id_usuario,
        publicacion_likes.c.id_usuario == usuario.id_usuario,
        publicacion_likes.c.fecha >= inicio_hoy,
    ).count()
    completada = likes_count >= 3
    misiones_progreso.append({
        'id': 'likes',
        'actual': min(likes_count, 3),
        'requisito': 3,
        'completada': completada,
        'reclamada': 'likes' in reclamadas,
    })
    if completada:
        misiones_completadas.append('likes')

    comment_count = Comentario.query.filter(
        Comentario.id_usuario == usuario.id_usuario,
        Comentario.fecha_creacion >= inicio_hoy,
    ).count()
    completada = comment_count >= 2
    misiones_progreso.append({
        'id': 'comentar',
        'actual': min(comment_count, 2),
        'requisito': 2,
        'completada': completada,
        'reclamada': 'comentar' in reclamadas,
    })
    if completada:
        misiones_completadas.append('comentar')

    return misiones_progreso, misiones_completadas

def reclamar_mision(usuario, mision_id):
    from app.factories.app_factory import db
    from app.models.transaccion import Transaccion

    reclamadas = _reclamadas_hoy(usuario)
    if mision_id in reclamadas:
        return {'success': False, 'message': 'Ya reclamaste esta misión hoy.'}

    prog, completadas = verificar_misiones(usuario)
    mision_data = next((m for m in MISIONES_DIARIAS if m['id'] == mision_id), None)
    if not mision_data:
        return {'success': False, 'message': 'Misión no encontrada.'}

    progreso = next((p for p in prog if p['id'] == mision_id), None)
    if not progreso or not progreso['completada']:
        return {'success': False, 'message': 'Aún no completas esta misión.'}

    if mision_id not in completadas:
        return {'success': False, 'message': 'Misión no disponible.'}

    reclamadas.add(mision_id)
    usuario.misiones_reclamadas_hoy = ','.join(sorted(reclamadas))
    usuario.ultimo_dia_misiones = date.today()

    usuario.tokens = (usuario.tokens or 0) + mision_data['tokens']
    tx = Transaccion(
        user_id=usuario.id_usuario,
        amount=mision_data['tokens'],
        tipo='ingreso',
        description=f'Misión diaria: {mision_data["nombre"]}',
    )
    db.session.add(tx)
    db.session.commit()

    return {
        'success': True,
        'tokens': mision_data['tokens'],
        'mision': mision_data['nombre'],
    }
