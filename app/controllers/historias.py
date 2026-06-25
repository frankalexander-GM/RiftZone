from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_login import login_required, current_user
from app.factories.app_factory import db
from app.models.transaccion import Historia as Story, HistoriaLike, HistoriaVista, HistoriaReaccion
from app.models.usuario import Usuario
from app.utils.avatar import avatar_url as resolve_avatar_url

historias_bp = Blueprint('historias', __name__, url_prefix='/historias')

EMOJIS_REACCION = ['❤️', '🔥', '😂', '😮', '😢', '💯', '🎮', '👏']

def _save_story_media(file):
    import os, uuid
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    filename = f'story_{uuid.uuid4().hex[:16]}.{ext}'
    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'stories')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return url_for('static', filename=f'uploads/stories/{filename}')

def _story_to_dict(h, usuario_actual_id=None):
    d = {
        'id': h.id_historia,
        'tipo': h.tipo,
        'archivo_url': h.archivo_url,
        'caption': h.caption,
        'color_fondo': h.color_fondo,
        'privacidad': h.privacidad,
        'created_at': h.created_at.isoformat(),
        'total_likes': h.total_likes,
        'total_vistas': h.total_vistas,
        'reacciones': {}
    }
    if usuario_actual_id:
        d['liked_by_me'] = h.liked_by(usuario_actual_id)
        d['visto_por_mi'] = h.visto_por(usuario_actual_id)
        mi_reaccion = HistoriaReaccion.query.filter_by(historia_id=h.id_historia, usuario_id=usuario_actual_id).first()
        d['mi_reaccion'] = mi_reaccion.emoji if mi_reaccion else None
    reacciones = db.session.query(HistoriaReaccion.emoji, db.func.count(HistoriaReaccion.id)).filter(
        HistoriaReaccion.historia_id == h.id_historia
    ).group_by(HistoriaReaccion.emoji).all()
    for emoji, count in reacciones:
        d['reacciones'][emoji] = count
    return d

@historias_bp.route('/feed', methods=['GET'])
@login_required
def feed():
    ahora = datetime.utcnow()
    historias = Story.query.filter(Story.expires_at > ahora).order_by(Story.created_at.desc()).all()
    agrupadas = {}
    for h in historias:
        u = h.usuario
        if h.privacidad == 'privado' and h.usuario_id != current_user.id_usuario:
            continue
        if h.privacidad == 'seguidores' and h.usuario_id != current_user.id_usuario:
            if not current_user.esta_siguiendo(u):
                continue
        if h.privacidad == 'amigos' and h.usuario_id != current_user.id_usuario:
            if not current_user.esta_siguiendo(u) or not u.esta_siguiendo(current_user):
                continue
        if u.id_usuario not in agrupadas:
            tiene_no_vistas = any(not h2.visto_por(current_user.id_usuario) for h2 in historias if h2.usuario_id == u.id_usuario)
            agrupadas[u.id_usuario] = {
                'id_usuario': u.id_usuario,
                'username': u.username,
                'nombre': u.nombre,
                'avatar': url_for('static', filename=u.foto_perfil.replace('/static/', '', 1)) if u.foto_perfil and u.foto_perfil.startswith('/static/') else (u.foto_perfil if u.foto_perfil else resolve_avatar_url(None)),
                'tiene_no_vistas': tiene_no_vistas,
                'historias': []
            }
        agrupadas[u.id_usuario]['historias'].append(_story_to_dict(h, current_user.id_usuario))
    return jsonify(list(agrupadas.values()))

@historias_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'message': 'Inicia sesión para crear historias.'}), 403

    tipo = request.form.get('tipo', 'image')
    caption = request.form.get('caption', '')
    color_fondo = request.form.get('color_fondo', '#7C3AED')
    privacidad = request.form.get('privacidad', 'publico')
    archivo_url = None

    if tipo in ('image', 'video'):
        file = request.files.get('archivo')
        if file:
            if tipo == 'image':
                allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            else:
                allowed = {'mp4', 'mov', 'avi', 'webm'}
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if ext not in allowed:
                return jsonify({'success': False, 'message': 'Formato no soportado.'}), 400
            archivo_url = _save_story_media(file)
        else:
            return jsonify({'success': False, 'message': 'Selecciona un archivo.'}), 400
    elif tipo == 'texto':
        if not caption:
            return jsonify({'success': False, 'message': 'Escribe algo para tu historia.'}), 400

    ahora = datetime.utcnow()
    story = Story(
        usuario_id=current_user.id_usuario,
        archivo_url=archivo_url,
        tipo=tipo,
        caption=caption,
        color_fondo=color_fondo,
        privacidad=privacidad,
        created_at=ahora,
        expires_at=ahora + timedelta(hours=24)
    )
    db.session.add(story)
    db.session.commit()
    return jsonify({'success': True, 'id': story.id_historia, 'story': _story_to_dict(story)})

@historias_bp.route('/usuario/<username>', methods=['GET'])
@login_required
def usuario_stories(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado.'}), 404
    ahora = datetime.utcnow()
    historias = Story.query.filter(
        Story.usuario_id == user.id_usuario,
        Story.expires_at > ahora
    ).order_by(Story.created_at.asc()).all()
    historias_filtradas = []
    for h in historias:
        if h.privacidad == 'privado' and h.usuario_id != current_user.id_usuario:
            continue
        if h.privacidad == 'seguidores' and h.usuario_id != current_user.id_usuario:
            if not current_user.esta_siguiendo(user):
                continue
        if h.privacidad == 'amigos' and h.usuario_id != current_user.id_usuario:
            if not current_user.esta_siguiendo(user) or not user.esta_siguiendo(current_user):
                continue
        historias_filtradas.append(_story_to_dict(h))
    return jsonify(historias_filtradas)

@historias_bp.route('/eliminar/<int:story_id>', methods=['POST'])
@login_required
def eliminar(story_id):
    story = Story.query.get_or_404(story_id)
    if story.usuario_id != current_user.id_usuario and not current_user.is_admin():
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403
    db.session.delete(story)
    db.session.commit()
    return jsonify({'success': True})

@historias_bp.route('/<int:story_id>/like', methods=['POST'])
@login_required
def toggle_like(story_id):
    story = Story.query.get_or_404(story_id)
    like = HistoriaLike.query.filter_by(historia_id=story_id, usuario_id=current_user.id_usuario).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'success': True, 'liked': False, 'total_likes': story.total_likes})
    like = HistoriaLike(historia_id=story_id, usuario_id=current_user.id_usuario)
    db.session.add(like)
    db.session.commit()
    return jsonify({'success': True, 'liked': True, 'total_likes': story.total_likes})

@historias_bp.route('/<int:story_id>/reaccion', methods=['POST'])
@login_required
def reaccionar(story_id):
    data = request.get_json()
    emoji = data.get('emoji', '❤️')
    existing = HistoriaReaccion.query.filter_by(historia_id=story_id, usuario_id=current_user.id_usuario).first()
    if existing:
        existing.emoji = emoji
    else:
        reaccion = HistoriaReaccion(historia_id=story_id, usuario_id=current_user.id_usuario, emoji=emoji)
        db.session.add(reaccion)
    db.session.commit()
    return jsonify({'success': True, 'emoji': emoji, 'mi_reaccion': emoji})

@historias_bp.route('/<int:story_id>/vista', methods=['POST'])
@login_required
def registrar_vista(story_id):
    story = Story.query.get_or_404(story_id)
    if not story.visto_por(current_user.id_usuario):
        vista = HistoriaVista(historia_id=story_id, usuario_id=current_user.id_usuario)
        db.session.add(vista)
        db.session.commit()
    return jsonify({'success': True, 'total_vistas': story.total_vistas})

@historias_bp.route('/<int:story_id>/responder', methods=['POST'])
@login_required
def responder(story_id):
    data = request.get_json()
    mensaje = (data.get('mensaje') or '').strip()
    if not mensaje:
        return jsonify({'success': False, 'message': 'Escribe un mensaje.'}), 400
    story = Story.query.get_or_404(story_id)
    from app.models.mensaje_privado import MensajePrivado
    msg = MensajePrivado(
        emisor_id=current_user.id_usuario,
        receptor_id=story.usuario_id,
        contenido=mensaje,
        leido=False
    )
    db.session.add(msg)
    notif = __import__('app.models.usuario', fromlist=['Notificacion']).Notificacion(
        usuario_id=story.usuario_id,
        mensaje=f'{current_user.nombre} respondió a tu historia',
        icono='fas fa-scroll',
        enlace='/mensajes'
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Respuesta enviada.'})

@historias_bp.route('/<int:story_id>/stats', methods=['GET'])
@login_required
def estadisticas(story_id):
    story = Story.query.get_or_404(story_id)
    if story.usuario_id != current_user.id_usuario and not current_user.is_admin():
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403
    vistas = HistoriaVista.query.filter_by(historia_id=story_id).order_by(HistoriaVista.created_at.desc()).limit(50).all()
    reacciones = db.session.query(HistoriaReaccion.emoji, db.func.count(HistoriaReaccion.id)).filter(
        HistoriaReaccion.historia_id == story_id
    ).group_by(HistoriaReaccion.emoji).all()
    return jsonify({
        'success': True,
        'total_vistas': story.total_vistas,
        'total_likes': story.total_likes,
        'reacciones': {e: c for e, c in reacciones},
        'usuarios_vieron': [{'username': v.usuario.username, 'avatar': resolve_avatar_url(v.usuario.foto_perfil)} for v in vistas]
    })

@historias_bp.route('/limpiar', methods=['POST'])
def limpiar_expiradas():
    ahora = datetime.utcnow()
    expiradas = Story.query.filter(Story.expires_at <= ahora).all()
    count = len(expiradas)
    for h in expiradas:
        db.session.delete(h)
    db.session.commit()
    return jsonify({'success': True, 'eliminadas': count})

@historias_bp.route('/usuarios_activos', methods=['GET'])
@login_required
def usuarios_con_historias():
    ahora = datetime.utcnow()
    historias = Story.query.filter(Story.expires_at > ahora).all()
    ids = set()
    for h in historias:
        if h.privacidad == 'privado' and h.usuario_id != current_user.id_usuario:
            continue
        if h.privacidad == 'seguidores' and h.usuario_id != current_user.id_usuario:
            if not current_user.esta_siguiendo(h.usuario):
                continue
        if h.privacidad == 'amigos' and h.usuario_id != current_user.id_usuario:
            if not current_user.esta_siguiendo(h.usuario) or not h.usuario.esta_siguiendo(current_user):
                continue
        ids.add(h.usuario_id)
    return jsonify({'user_ids': list(ids)})

@historias_bp.route('/<int:story_id>/privacidad', methods=['POST'])
@login_required
def cambiar_privacidad(story_id):
    story = Story.query.get_or_404(story_id)
    if story.usuario_id != current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403
    data = request.get_json()
    privacidad = data.get('privacidad', 'publico')
    if privacidad not in ('publico', 'seguidores', 'amigos', 'privado'):
        return jsonify({'success': False, 'message': 'Privacidad inválida.'}), 400
    story.privacidad = privacidad
    db.session.commit()
    return jsonify({'success': True, 'privacidad': privacidad})

@historias_bp.route('/<int:story_id>/reportar', methods=['POST'])
@login_required
def reportar(story_id):
    story = Story.query.get_or_404(story_id)
    data = request.get_json() or {}
    motivo = data.get('motivo', 'inapropiado')
    report = __import__('app.models.transaccion', fromlist=['ReporteHistoria'])
    reporte = report.ReporteHistoria(
        historia_id=story_id,
        usuario_id=current_user.id_usuario,
        motivo=motivo,
        created_at=datetime.utcnow()
    )
    db.session.add(reporte)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Historia reportada.'})

@historias_bp.route('/<int:story_id>/bloquear', methods=['POST'])
@login_required
def bloquear_usuario(story_id):
    story = Story.query.get_or_404(story_id)
    if story.usuario_id == current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No puedes bloquearte a ti mismo.'}), 400
    bloqueo = __import__('app.models.transaccion', fromlist=['BloqueoUsuario'])
    existente = bloqueo.BloqueoUsuario.query.filter_by(
        usuario_id=current_user.id_usuario,
        bloqueado_id=story.usuario_id
    ).first()
    if not existente:
        b = bloqueo.BloqueoUsuario(usuario_id=current_user.id_usuario, bloqueado_id=story.usuario_id)
        db.session.add(b)
        db.session.commit()
    return jsonify({'success': True, 'message': 'Usuario bloqueado.'})

@historias_bp.route('/<int:story_id>/silenciar', methods=['POST'])
@login_required
def silenciar_usuario(story_id):
    story = Story.query.get_or_404(story_id)
    if story.usuario_id == current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No puedes silenciarte.'}), 400
    silencio = __import__('app.models.transaccion', fromlist=['SilencioUsuario'])
    existente = silencio.SilencioUsuario.query.filter_by(
        usuario_id=current_user.id_usuario,
        silenciado_id=story.usuario_id
    ).first()
    if not existente:
        s = silencio.SilencioUsuario(usuario_id=current_user.id_usuario, silenciado_id=story.usuario_id)
        db.session.add(s)
        db.session.commit()
    return jsonify({'success': True, 'message': 'Usuario silenciado.'})

@historias_bp.route('/<int:story_id>/destacar', methods=['POST'])
@login_required
def destacar(story_id):
    story = Story.query.get_or_404(story_id)
    if story.usuario_id != current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403
    story.destacada = not getattr(story, 'destacada', False)
    db.session.commit()
    return jsonify({'success': True, 'destacada': story.destacada})

@historias_bp.route('/<int:story_id>/guardar', methods=['POST'])
@login_required
def guardar(story_id):
    Story.query.get_or_404(story_id)
    guardado = __import__('app.models.transaccion', fromlist=['HistoriaGuardada'])
    existente = guardado.HistoriaGuardada.query.filter_by(
        historia_id=story_id,
        usuario_id=current_user.id_usuario
    ).first()
    if existente:
        db.session.delete(existente)
        db.session.commit()
        return jsonify({'success': True, 'guardado': False})
    g = guardado.HistoriaGuardada(historia_id=story_id, usuario_id=current_user.id_usuario)
    db.session.add(g)
    db.session.commit()
    return jsonify({'success': True, 'guardado': True})

@historias_bp.route('/<int:story_id>/respuestas', methods=['GET'])
@login_required
def respuestas(story_id):
    story = Story.query.get_or_404(story_id)
    if story.usuario_id != current_user.id_usuario and not current_user.is_admin():
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403
    from app.models.mensaje_privado import MensajePrivado
    msgs = MensajePrivado.query.filter_by(receptor_id=current_user.id_usuario).order_by(MensajePrivado.created_at.desc()).limit(20).all()
    return jsonify({
        'success': True,
        'respuestas': [{'username': m.emisor.username, 'mensaje': m.contenido, 'created_at': m.created_at.isoformat()} for m in msgs]
    })
