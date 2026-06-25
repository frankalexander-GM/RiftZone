from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user, login_user

jugador_bp = Blueprint('jugador', __name__, template_folder='../templates/jugador')

@jugador_bp.route('/dashboard')
@login_required
def dashboard():
    tab = request.args.get('tab', 'para-ti')
    valid_tabs = ('para-ti', 'siguiendo', 'populares', 'videos', 'encuestas', 'recientes')
    if tab not in valid_tabs:
        tab = 'para-ti'
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    publicaciones = pub_service.obtener_feed(tab=tab, user_id=current_user.id_usuario)
    return render_template('dashboard/inicio/inicio.html', publicaciones=publicaciones, active_tab=tab)

@jugador_bp.route('/api/feed')
@login_required
def api_feed():
    tab = request.args.get('tab', 'para-ti')
    valid_tabs = ('para-ti', 'siguiendo', 'populares', 'videos', 'encuestas', 'recientes')
    if tab not in valid_tabs:
        tab = 'para-ti'
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    publicaciones = pub_service.obtener_feed(tab=tab, user_id=current_user.id_usuario)
    posts_json = []
    from app.utils.avatar import avatar_url
    for p in publicaciones:
        post_data = {
            'id_publicacion': p.id_publicacion,
            'contenido': p.contenido,
            'juego': p.juego,
            'imagen_url': p.imagen_url,
            'video_archivo': p.video_archivo,
            'fecha_creacion': p.fecha_creacion.isoformat() if p.fecha_creacion else None,
            'likes_count': p.likes,
            'comentarios_count': len(p.comentarios),
            'fijada': p.fijada,
            'promocionada': p.promocionada,
            'boost_tipo': p.boost_tipo,
            'is_poll': p.is_poll,
            'autor': {
                'username': p.autor.username,
                'nombre': p.autor.nombre or p.autor.username,
                'foto_perfil': avatar_url(p.autor.foto_perfil),
                'id': p.autor.id_usuario,
            },
            'liked': current_user in p.usuarios_likes,
            'repost_id': p.repost_id,
            'reposteado': None,
            'poll': None,
        }
        if p.repost_id and p.reposteado:
            orig = p.reposteado
            orig_poll = None
            if orig.is_poll and orig.poll:
                options = [{'id': o.id_option, 'texto': o.texto, 'votos': o.votos} for o in orig.poll.options]
                orig_poll = {
                    'pregunta': orig.poll.pregunta,
                    'multiple_choice': orig.poll.multiple_choice,
                    'total_votos': orig.poll.total_votos,
                    'options': options,
                }
            post_data['reposteado'] = {
                'id_publicacion': orig.id_publicacion,
                'contenido': orig.contenido[:300] + ('...' if len(orig.contenido or '') > 300 else ''),
                'juego': orig.juego,
                'imagen_url': orig.imagen_url,
                'video_archivo': orig.video_archivo,
                'is_poll': orig.is_poll,
                'poll': orig_poll,
                'autor': {
                    'username': orig.autor.username,
                    'nombre': orig.autor.nombre or orig.autor.username,
                    'foto_perfil': avatar_url(orig.autor.foto_perfil),
                    'id': orig.autor.id_usuario,
                },
            }
        if p.is_poll and p.poll:
            options = [{'id': o.id_option, 'texto': o.texto, 'votos': o.votos} for o in p.poll.options]
            post_data['poll'] = {
                'pregunta': p.poll.pregunta,
                'multiple_choice': p.poll.multiple_choice,
                'total_votos': p.poll.total_votos,
                'options': options,
            }
        posts_json.append(post_data)
    return jsonify({'posts': posts_json, 'tab': tab})


@jugador_bp.route('/explorar')
def explorar():
    from app.models.publicacion import Publicacion
    from sqlalchemy import func
    from app.data.game_categories import get_game_categories
    juegos_top = (
        db_session().query(Publicacion.juego, func.count(Publicacion.juego).label('cnt'))
        .filter(Publicacion.juego != None, Publicacion.juego != '')
        .group_by(Publicacion.juego)
        .order_by(func.count(Publicacion.juego).desc())
        .limit(10).all()
    )
    # Build full community list with colors
    todas_comunidades = []
    gcolor_map = {}
    for cat in get_game_categories():
        for g in cat['juegos']:
            gcolor_map[g['nombre'].lower()] = {'color': cat['color'], 'categoria': cat['titulo']}
    for j, cnt in juegos_top:
        info = gcolor_map.get(j.lower(), {})
        todas_comunidades.append({
            'nombre': j,
            'color': info.get('color', '#8b5cf6'),
            'categoria': info.get('categoria', 'General'),
            'posts': cnt,
        })
    categorias = sorted(set(c['categoria'] for c in todas_comunidades))
    return render_template('jugador/explorar.html',
        juegos_top=juegos_top,
        todas_comunidades=todas_comunidades,
        categorias=categorias)


def db_session():
    from app.factories.app_factory import db
    return db.session


@jugador_bp.route('/api/explorar/buscar')
def api_explorar_buscar():
    from app.models.usuario import Usuario
    from app.models.publicacion import Publicacion
    from app.utils.avatar import avatar_url
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'usuarios': [], 'publicaciones': []})

    pattern = f'%{q}%'
    usuarios = Usuario.query.filter(
        (Usuario.username.ilike(pattern)) | (Usuario.nombre.ilike(pattern))
    ).limit(8).all()

    publicaciones = Publicacion.query.filter(
        (Publicacion.contenido.ilike(pattern)) | (Publicacion.juego.ilike(pattern))
    ).order_by(Publicacion.fecha_creacion.desc()).limit(6).all()

    user_id = current_user.id_usuario if current_user.is_authenticated else None
    siguiendo_ids = set()
    if current_user.is_authenticated:
        siguiendo_ids = {u.id_usuario for u in current_user.siguiendo.all()}

    def u_dict(u):
        return {
            'id': u.id_usuario,
            'username': u.username,
            'nombre': u.nombre or u.username,
            'foto': avatar_url(u.foto_perfil),
            'nivel': u.nivel,
            'seguidores': u.num_seguidores,
            'siguiendo': u.id_usuario in siguiendo_ids,
            'url': url_for('jugador.perfil_publico', username=u.username),
        }

    def p_dict(p):
        return {
            'id': p.id_publicacion,
            'contenido': (p.contenido or '')[:200],
            'juego': p.juego,
            'imagen_url': p.imagen_url,
            'likes': p.likes_count,
            'comentarios': p.comentarios_count,
            'liked': current_user.is_authenticated and p.is_liked_by(current_user),
            'shares': p.shares_count or 0,
            'autor': {
                'username': p.autor.username,
                'nombre': p.autor.nombre or p.autor.username,
                'foto': avatar_url(p.autor.foto_perfil),
            },
            'url': url_for('jugador.ver_publicacion', post_id=p.id_publicacion),
            'autor_url': url_for('jugador.perfil_publico', username=p.autor.username),
        }

    return jsonify({
        'usuarios': [u_dict(u) for u in usuarios],
        'publicaciones': [p_dict(p) for p in publicaciones],
    })


@jugador_bp.route('/api/explorar/tab/<tab>')
def api_explorar_tab(tab):
    from app.models.publicacion import Publicacion
    from app.utils.avatar import avatar_url
    from sqlalchemy import func

    offset = request.args.get('offset', 0, type=int)
    limit = min(request.args.get('limit', 20, type=int), 50)

    def p_dict(p):
        return {
            'id': p.id_publicacion,
            'contenido': (p.contenido or '')[:300],
            'juego': p.juego,
            'imagen_url': p.imagen_url,
            'video_archivo': p.video_archivo,
            'likes': p.likes_count,
            'comentarios': p.comentarios_count,
            'liked': p.is_liked_by(current_user),
            'shares': p.shares_count or 0,
            'autor': {
                'username': p.autor.username,
                'nombre': p.autor.nombre or p.autor.username,
                'foto': avatar_url(p.autor.foto_perfil),
            },
            'url': url_for('jugador.ver_publicacion', post_id=p.id_publicacion),
            'autor_url': url_for('jugador.perfil_publico', username=p.autor.username),
        }

    def get_total(tab):
        if tab == 'tendencias':
            return db_session().query(Publicacion.juego).filter(
                Publicacion.juego != None, Publicacion.juego != ''
            ).distinct().count()
        elif tab == 'clips':
            return Publicacion.query.filter(Publicacion.video_archivo != None).count()
        elif tab == 'imagenes':
            return Publicacion.query.filter(Publicacion.imagen_url != None).count()
        return 0

    total = get_total(tab)
    has_more = (offset + limit) < total

    if tab == 'tendencias':
        half = limit // 2
        juegos = (
            db_session().query(Publicacion.juego, func.count(Publicacion.juego).label('cnt'))
            .filter(Publicacion.juego != None, Publicacion.juego != '')
            .group_by(Publicacion.juego)
            .order_by(func.count(Publicacion.juego).desc())
            .all()
        )
        all_pubs = Publicacion.query.order_by(Publicacion.fecha_creacion.desc()).limit(50).all()
        all_pubs.sort(key=lambda p: (p.likes_count or 0) + (p.comentarios_count or 0) + (p.shares_count or 0), reverse=True)
        top_pubs = all_pubs[:half]
        items = []
        items.append({'type': 'games_section'})
        for j, c in juegos[:half]:
            items.append({'type': 'game', 'juego': j, 'posts': c})
        items.append({'type': 'posts_section'})
        for p in top_pubs[:half]:
            pd = p_dict(p)
            pd['type'] = 'post'
            items.append(pd)
        # Top 4 comunidades con sus posts destacados
        from app.data.game_categories import get_game_categories
        gcolor_map = {}
        for cat in get_game_categories():
            for g in cat['juegos']:
                gcolor_map[g['nombre'].lower()] = cat['color']
        top4 = juegos[:4]
        top_comunidades = []
        seen_ids = set()
        for j, cnt in top4:
            community_pubs = Publicacion.query.filter(
                Publicacion.juego == j
            ).order_by(Publicacion.fecha_creacion.desc()).limit(4).all()
            community_pubs.sort(key=lambda p: (p.likes_count or 0) + (p.comentarios_count or 0) + (p.shares_count or 0), reverse=True)
            posts = []
            for cp in community_pubs[:3]:
                pd = p_dict(cp)
                seen_ids.add(cp.id_publicacion)
                posts.append(pd)
            if posts:
                top_comunidades.append({
                    'juego': j,
                    'color': gcolor_map.get(j.lower(), '#8b5cf6'),
                    'posts': posts,
                    'total': cnt,
                })
        has_more = False
        return jsonify({
            'tab': tab, 'items': items, 'has_more': has_more, 'total': len(items),
            'top_comunidades': top_comunidades,
        })

    elif tab == 'clips':
        clips = Publicacion.query.filter(
            Publicacion.video_archivo != None
        ).order_by(Publicacion.fecha_creacion.desc()).offset(offset).limit(limit).all()
        return jsonify({'tab': tab, 'items': [p_dict(p) for p in clips], 'has_more': has_more, 'total': total})

    elif tab == 'imagenes':
        imgs = Publicacion.query.filter(
            Publicacion.imagen_url != None
        ).order_by(Publicacion.fecha_creacion.desc()).offset(offset).limit(limit).all()
        return jsonify({'tab': tab, 'items': [p_dict(p) for p in imgs], 'has_more': has_more, 'total': total})

    elif tab == 'post':
        post_id = request.args.get('id', type=int)
        if post_id:
            post = Publicacion.query.get(post_id)
            if post:
                return jsonify({'tab': tab, 'items': [p_dict(post)], 'has_more': False, 'total': 1})
        return jsonify({'tab': tab, 'items': [], 'has_more': False, 'total': 0})

    pubs = Publicacion.query.order_by(Publicacion.fecha_creacion.desc()).offset(offset).limit(limit).all()
    return jsonify({'tab': tab, 'items': [p_dict(p) for p in pubs], 'has_more': has_more, 'total': total})

@jugador_bp.route('/crear-publicacion', methods=['POST'])
@login_required
def crear_publicacion():
    from app.factories.service_factory import get_service_factory
    from app.factories.app_factory import db
    from flask import current_app
    from app.models.publicacion import Poll, PollOption
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    
    from app.utils.profanity import filter_profanity
    contenido = filter_profanity(request.form.get('contenido', '').strip())
    juego = request.form.get('juego')
    tipo_post = request.form.get('tipo_post', 'texto')
    imagen_url = request.form.get('imagen_url', '').strip()
    imagen_archivo = request.files.get('imagen_archivo')
    video_archivo = request.files.get('video_archivo')
    clip_url = request.form.get('clip_url', '').strip()
    clip_archivo = request.files.get('clip_archivo')

    def _save_upload(file, subdir='images'):
        import os, uuid
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
        filename = f'post_{uuid.uuid4().hex[:12]}.{ext}'
        upload_dir = os.path.join(current_app.static_folder, 'uploads', subdir)
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        return '/static/uploads/' + subdir + '/' + filename

    video_archivo_path = None

    # File upload priority: video_archivo > imagen_archivo > imagen_url > clip_url
    if video_archivo and video_archivo.filename:
        ext = video_archivo.filename.rsplit('.', 1)[-1].lower() if '.' in video_archivo.filename else ''
        if ext not in ('mp4', 'mov', 'avi') or not video_archivo.content_type.startswith('video/'):
            flash('El archivo no es un video válido (solo .mp4, .mov, .avi).', 'error')
            return redirect(url_for('jugador.dashboard'))
        video_archivo_path = _save_upload(video_archivo, 'videos')
        imagen_url = video_archivo_path
    elif imagen_archivo and imagen_archivo.filename:
        ext = imagen_archivo.filename.rsplit('.', 1)[-1].lower() if '.' in imagen_archivo.filename else ''
        allowed_img = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg'})
        if ext not in allowed_img or not imagen_archivo.content_type.startswith('image/'):
            flash('El archivo no es una imagen válida (solo .png, .jpg, .jpeg).', 'error')
            return redirect(url_for('jugador.dashboard'))
        imagen_url = _save_upload(imagen_archivo, 'images')

    poll_data = None

    # Build content based on type
    if tipo_post == 'clip':
        # Clip as file upload
        if clip_archivo and clip_archivo.filename:
            ext = clip_archivo.filename.rsplit('.', 1)[-1].lower() if '.' in clip_archivo.filename else ''
            if ext not in ('mp4', 'mov') or not clip_archivo.content_type.startswith('video/'):
                flash('El clip debe ser un video .mp4 o .mov.', 'error')
                return redirect(url_for('jugador.dashboard'))
            video_archivo_path = _save_upload(clip_archivo, 'clips')
            imagen_url = video_archivo_path
            contenido = contenido or '[Clip]'
        elif clip_url and not imagen_url:
            contenido = f'[Clip] {clip_url}'
            imagen_url = clip_url
        elif imagen_url:
            contenido = contenido or '[Clip]'
    
    elif tipo_post == 'poll':
        pregunta = request.form.get('poll_pregunta', '').strip()
        opciones = [v.strip() for v in request.form.getlist('poll_op[]') if v.strip()]
        if pregunta and len(opciones) >= 2:
            contenido = pregunta
            poll_data = {
                'pregunta': pregunta,
                'opciones': opciones,
                'duracion': request.form.get('poll_duration', '24h'),
                'hide_results': bool(request.form.get('poll_hide_results')),
            }
        elif not contenido:
            contenido = '[Encuesta]'
    
    try:
        post = pub_service.crear_publicacion(
            id_usuario=current_user.id_usuario,
            contenido=contenido or 'Publicación',
            juego=juego,
            imagen_url=imagen_url or None,
            video_archivo=video_archivo_path or None
        )
        
        # Save poll to DB
        if poll_data:
            poll = Poll(
                id_publicacion=post.id_publicacion,
                pregunta=poll_data['pregunta'],
                multiple_choice=bool(request.form.get('poll_multiple')),
                allow_change=bool(request.form.get('poll_change')),
                hide_results=poll_data.get('hide_results', False),
                duracion=poll_data.get('duracion', '24h'),
            )
            db.session.add(poll)
            db.session.flush()
            for texto in poll_data['opciones']:
                opt = PollOption(id_poll=poll.id_poll, texto=texto)
                db.session.add(opt)
            db.session.commit()
        
        flash('Publicación creada con éxito.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
        if _wants_json():
            return jsonify({'success': False, 'message': str(e)}), 400
    
    if _wants_json():
        from app.models.usuario import Usuario
        autor = Usuario.query.get(post.id_usuario)
        post_response = {
            'id_publicacion': post.id_publicacion,
            'contenido': post.contenido,
            'juego': post.juego,
            'imagen_url': post.imagen_url,
            'video_archivo': post.video_archivo,
            'fecha_creacion': post.fecha_creacion.isoformat() if post.fecha_creacion else None,
            'autor': {
                'id_usuario': autor.id_usuario,
                'username': autor.username,
                'nombre': autor.nombre,
                'foto_perfil': url_for('static', filename=f'uploads/avatars/{autor.foto_perfil}') if autor.foto_perfil else None
            }
        }
        if post.is_poll and post.poll:
            poll_response = {
                'is_poll': True,
                'poll': {
                    'pregunta': post.poll.pregunta,
                    'multiple_choice': post.poll.multiple_choice,
                    'allow_change': post.poll.allow_change,
                    'hide_results': post.poll.hide_results,
                    'options': [{'id': o.id_option, 'texto': o.texto, 'votos': o.votos} for o in post.poll.options]
                }
            }
            post_response.update(poll_response)
        return jsonify({
            'success': True,
            'post': post_response
        })
    
    return redirect(url_for('jugador.dashboard'))



def _wants_json():
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or request.is_json
    )


@jugador_bp.route('/comentar/<int:post_id>', methods=['POST'])
@login_required
def comentar(post_id):
    from flask import jsonify
    from app.factories.service_factory import get_service_factory
    from app.models.comentario import Comentario
    from app.utils.avatar import avatar_url

    if current_user.rol == 'invitado':
        if _wants_json():
            return jsonify({'success': False, 'message': 'Regístrate para comentar.'}), 403
        flash('Debes registrarte para comentar.', 'error')
        from urllib.parse import urlparse
        ref = request.referrer
        if ref:
            parsed = urlparse(ref)
            if parsed.netloc and parsed.netloc != request.host:
                ref = None
        return redirect(ref or url_for('jugador.dashboard'))

    from app.utils.profanity import filter_profanity
    sf = get_service_factory()
    com_service = sf.get_comentario_service()
    contenido = filter_profanity((request.form.get('contenido') or '').strip())
    if not contenido and request.is_json:
        contenido = filter_profanity(((request.get_json(silent=True) or {}).get('contenido', '')).strip())

    try:
        com = com_service.crear_comentario(
            id_publicacion=post_id,
            id_usuario=current_user.id_usuario,
            contenido=contenido,
        )
        comments_count = Comentario.query.filter_by(id_publicacion=post_id).count()

        from app.models.publicacion import Publicacion
        post = Publicacion.query.get(post_id)
        if post and post.usuario_id != current_user.id_usuario:
            try:
                notif = sf.get_notificacion_service()
                notif.crear_notificacion(
                    usuario_id=post.usuario_id,
                    tipo='comentario',
                    mensaje=f'{current_user.nombre or current_user.username} comentó tu publicación',
                    enlace=url_for('jugador.comunidad_detalle', juego=post.juego) + '#comments-' + str(post_id),
                )
            except:
                pass

        if _wants_json():
            return jsonify({
                'success': True,
                'comments_count': comments_count,
                'comment': {
                    'autor_nombre': current_user.nombre or current_user.username,
                    'contenido': com.contenido,
                    'fecha': com.fecha_creacion.strftime('%d/%m/%Y'),
                    'foto': avatar_url(current_user.foto_perfil),
                },
            })

        flash('Comentario publicado.', 'success')
        from urllib.parse import urlparse
        ref = request.referrer
        if ref:
            parsed = urlparse(ref)
            if parsed.netloc and parsed.netloc != request.host:
                ref = None
        referrer = ref or url_for('jugador.dashboard')
        return redirect(f'{referrer.split("#")[0]}#comments-{post_id}')
    except ValueError as e:
        if _wants_json():
            return jsonify({'success': False, 'message': str(e)}), 400
        flash(str(e), 'error')
        from urllib.parse import urlparse
        ref = request.referrer
        if ref:
            parsed = urlparse(ref)
            if parsed.netloc and parsed.netloc != request.host:
                ref = None
        return redirect(ref or url_for('jugador.dashboard'))


@jugador_bp.route('/poll/vote/<int:post_id>', methods=['POST'])
@login_required
def poll_vote(post_id):
    from flask import jsonify
    from app.models.publicacion import Poll, PollOption, PollVote
    from app.factories.app_factory import db
    
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'message': 'Regístrate para votar.'}), 403
    
    poll = Poll.query.filter_by(id_publicacion=post_id).first()
    if not poll:
        return jsonify({'success': False, 'message': 'Encuesta no encontrada.'}), 404
    
    option_id = request.form.get('option_id', type=int) or (request.get_json(silent=True) or {}).get('option_id')
    if not option_id:
        return jsonify({'success': False, 'message': 'Selecciona una opción.'}), 400
    
    # Check option belongs to this poll
    option = PollOption.query.filter_by(id_option=option_id, id_poll=poll.id_poll).first()
    if not option:
        return jsonify({'success': False, 'message': 'Opción inválida.'}), 400
    
    # Get user's existing votes for this poll
    existing_votes = PollVote.query.filter(
        PollVote.id_option.in_([o.id_option for o in poll.options]),
        PollVote.id_usuario == current_user.id_usuario
    ).all()
    
    already_voted_this = any(v.id_option == option_id for v in existing_votes)
    
    if already_voted_this:
        if poll.allow_change:
            # Remove this vote
            for v in existing_votes:
                if v.id_option == option_id:
                    db.session.delete(v)
                    option.votos -= 1
                    break
            db.session.commit()
            voted_ids = [v.id_option for v in PollVote.query.filter(
                PollVote.id_option.in_([o.id_option for o in poll.options]),
                PollVote.id_usuario == current_user.id_usuario
            ).all()]
            results = _build_poll_results(poll)
            return jsonify({'success': True, 'total_votos': poll.total_votos, 'results': results, 'voted_options': voted_ids, 'removed': True})
        else:
            return jsonify({'success': False, 'message': 'Ya votaste esta opción.'}), 409
    
    if existing_votes and not poll.multiple_choice:
        if poll.allow_change:
            # Remove all previous votes, then add new
            for v in existing_votes:
                old_opt = PollOption.query.get(v.id_option)
                if old_opt:
                    old_opt.votos -= 1
                db.session.delete(v)
        else:
            return jsonify({'success': False, 'message': 'Solo puedes elegir una opción.'}), 409
    
    vote = PollVote(id_option=option_id, id_usuario=current_user.id_usuario)
    option.votos += 1
    db.session.add(vote)
    db.session.commit()
    
    voted_ids = [v.id_option for v in PollVote.query.filter(
        PollVote.id_option.in_([o.id_option for o in poll.options]),
        PollVote.id_usuario == current_user.id_usuario
    ).all()]
    
    results = _build_poll_results(poll)
    
    return jsonify({
        'success': True,
        'total_votos': poll.total_votos,
        'results': results,
        'voted_options': voted_ids
    })


def _build_poll_results(poll):
    results = []
    for opt in poll.options:
        results.append({
            'id': opt.id_option,
            'texto': opt.texto,
            'votos': opt.votos,
            'porcentaje': round((opt.votos / poll.total_votos * 100)) if poll.total_votos > 0 else 0
        })
    return results


@jugador_bp.route('/repost/<int:post_id>', methods=['POST'])
@login_required
def repost(post_id):
    from flask import jsonify
    from app.factories.service_factory import get_service_factory
    from app.factories.app_factory import db

    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'message': 'Regístrate para repostear.'}), 403

    from app.models.publicacion import Publicacion
    original = Publicacion.query.get(post_id)
    if not original:
        return jsonify({'success': False, 'message': 'Publicación no encontrada.'}), 404

    # Walk up the repost chain to find the ROOT original
    root = original
    seen = set()
    while root.repost_id and root.reposteado and root.id_publicacion not in seen:
        seen.add(root.id_publicacion)
        root = root.reposteado
    root_id = root.id_publicacion

    from app.utils.profanity import filter_profanity
    data = request.get_json(silent=True) or {}
    contenido = filter_profanity((data.get('contenido') or '').strip())
    juego_destino = (data.get('juego_destino') or '').strip()

    if juego_destino and juego_destino != 'perfil':
        juego_final = juego_destino
    else:
        juego_final = original.juego or ''

    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    try:
        new_post = Publicacion(
            id_usuario=current_user.id_usuario,
            contenido=contenido or '[Repost]',
            juego=juego_final,
            repost_id=root_id,
        )
        db.session.add(new_post)
        db.session.commit()

        # Reload with relationships for real-time response
        from app.utils.avatar import avatar_url
        from sqlalchemy.orm import joinedload
        full = Publicacion.query.options(
            joinedload(Publicacion.autor),
            joinedload(Publicacion.reposteado).joinedload(Publicacion.autor),
        ).get(new_post.id_publicacion)

        if _wants_json():
            return jsonify({
                'success': True,
                'post_id': new_post.id_publicacion,
                'post': {
                    'id': full.id_publicacion,
                    'contenido': full.contenido,
                    'juego': full.juego,
                    'fecha': full.fecha_creacion.isoformat() if full.fecha_creacion else '',
                    'autor': {
                        'username': full.autor.username,
                        'nombre': full.autor.nombre or full.autor.username,
                        'foto': avatar_url(full.autor.foto_perfil),
                    },
                    'reposteado': {
                        'id': full.reposteado.id_publicacion,
                        'contenido': full.reposteado.contenido,
                        'imagen_url': full.reposteado.imagen_url,
                        'video_archivo': full.reposteado.video_archivo,
                        'autor': {
                            'username': full.reposteado.autor.username,
                            'nombre': full.reposteado.autor.nombre or full.reposteado.autor.username,
                            'foto': avatar_url(full.reposteado.autor.foto_perfil),
                        },
                    } if full.reposteado else None,
                }
            })
        flash('¡Publicación reposteada!', 'success')
    except Exception as e:
        db.session.rollback()
        if _wants_json():
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(str(e), 'error')
    return redirect(url_for('jugador.dashboard'))


@jugador_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    from flask import jsonify
    from app.factories.service_factory import get_service_factory

    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'message': 'Regístrate para dar like.'}), 403

    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()

    try:
        liked = pub_service.toggle_like(post_id, current_user)
        post = pub_service.pub_repo.get_by_id(post_id)
        if not post:
            return jsonify({'success': False, 'message': 'Publicación no encontrada.'}), 404
        likes_count = len(post.usuarios_likes)

        if liked and post.usuario_id != current_user.id_usuario:
            try:
                notif = sf.get_notificacion_service()
                notif.crear_notificacion(
                    usuario_id=post.usuario_id,
                    tipo='like',
                    mensaje=f'a {current_user.nombre or current_user.username} le gusta tu publicación',
                    enlace=url_for('jugador.comunidad_detalle', juego=post.juego) + '#post-' + str(post_id),
                )
            except:
                pass

        return jsonify({'success': True, 'liked': liked, 'likes_count': likes_count})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception:
        from app.factories.app_factory import db
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al procesar el like.'}), 500

@jugador_bp.route('/share/<int:post_id>', methods=['POST'])
@login_required
def share_post(post_id):
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    post = pub_service.pub_repo.get_by_id(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'Publicación no encontrada.'}), 404
    post.shares_count = (post.shares_count or 0) + 1
    from app.factories.app_factory import db
    db.session.commit()
    return jsonify({'success': True, 'shares_count': post.shares_count})

@jugador_bp.route('/api/post/<int:post_id>')
@login_required
def api_post(post_id):
    from app.factories.service_factory import get_service_factory
    from app.utils.avatar import avatar_url
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    post = pub_service.pub_repo.get_by_id(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'No encontrada.'}), 404
    return jsonify({
        'success': True,
        'post': {
            'contenido': post.contenido,
            'imagen': post.imagen_url,
            'video': post.video_archivo,
            'author': post.autor.nombre or post.autor.username,
            'username': post.autor.username,
            'avatar': avatar_url(post.autor.foto_perfil),
        }
    })

@jugador_bp.route('/promocionar/<int:post_id>', methods=['POST'])
@login_required
def promocionar(post_id):
    flash('Elige un plan de boost en la Central de Boosts.', 'success')
    return redirect(url_for('jugador.boosts', post_id=post_id))

@jugador_bp.route('/boosts')
@login_required
def boosts():
    from datetime import datetime
    from app.models.publicacion import Publicacion
    from app.models.transaccion import Transaccion
    from app.services.boost_service import BOOST_PLANS

    post_id = request.args.get('post_id', type=int)
    post = None
    if post_id:
        from app.factories.service_factory import get_service_factory
        sf = get_service_factory()
        pub_service = sf.get_publicacion_service()
        post = pub_service.pub_repo.get_by_id(post_id)
        if post and post.id_usuario != current_user.id_usuario:
            post = None
            flash('Solo puedes boostear tus propias publicaciones.', 'error')

    mis_posts = (
        Publicacion.query.filter_by(id_usuario=current_user.id_usuario)
        .order_by(Publicacion.fecha_creacion.desc())
        .limit(20)
        .all()
    )

    now = datetime.utcnow()
    boosts_activos = Publicacion.query.filter(
        Publicacion.id_usuario == current_user.id_usuario,
        Publicacion.promocionada.is_(True),
        Publicacion.boost_hasta.isnot(None),
        Publicacion.boost_hasta > now,
    ).order_by(Publicacion.boost_hasta.asc()).all()

    historial = Transaccion.query.filter(
        Transaccion.user_id == current_user.id_usuario,
        Transaccion.tipo == 'egreso',
        Transaccion.description.ilike('%boost%'),
    ).order_by(Transaccion.created_at.desc()).limit(10).all()

    return render_template(
        'jugador/boosts.html',
        post_target=post,
        mis_posts=mis_posts,
        boost_planes=BOOST_PLANS,
        saldo=current_user.tokens or 0,
        boosts_activos=boosts_activos,
        historial=historial,
    )


@jugador_bp.route('/comprar-boost', methods=['POST'])
@login_required
def comprar_boost():
    if current_user.rol == 'invitado':
        msg = 'Regístrate para usar boosts.'
        return jsonify({'success': False, 'message': msg}) if _wants_json() else (flash(msg, 'error') or redirect(url_for('jugador.boosts')))

    plan = (request.form.get('plan') or '').strip()
    post_id = request.form.get('post_id', type=int)

    if not post_id:
        msg = 'Selecciona una publicación para boostear.'
        return jsonify({'success': False, 'message': msg}) if _wants_json() else (flash(msg, 'error') or redirect(url_for('jugador.boosts')))

    try:
        from app.services.boost_service import aplicar_boost
        from flask_login import login_user
        from app.factories.app_factory import db

        post, plan_info = aplicar_boost(current_user, post_id, plan)
        db.session.refresh(current_user)
        if _wants_json():
            return jsonify({'success': True, 'nuevo_saldo': current_user.tokens, 'plan': plan_info})
        flash(f'¡{plan_info["nombre"]} activado! Saldo: {current_user.tokens} RC.', 'success')
        return redirect(url_for('jugador.dashboard'))
    except ValueError as e:
        msg = str(e)
        return jsonify({'success': False, 'message': msg}) if _wants_json() else (flash(msg, 'error') or redirect(url_for('jugador.boosts', post_id=post_id)))
    except Exception:
        from app.factories.app_factory import db
        db.session.rollback()
        msg = 'Error al aplicar el boost.'
        return jsonify({'success': False, 'message': msg}) if _wants_json() else (flash(msg, 'error') or redirect(url_for('jugador.boosts', post_id=post_id)))

@jugador_bp.route('/premium')
@login_required
def premium():
    from app.utils.vip import planes_reclamados, PLANES_VIP
    reclamados = planes_reclamados(current_user.id_usuario)
    return render_template(
        'jugador/premium.html',
        planes_reclamados=reclamados,
        planes_vip=PLANES_VIP,
    )

@jugador_bp.route('/comprar-premium', methods=['POST'])
@login_required
def comprar_premium():
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'message': 'Invitados no pueden comprar premium.'}), 403

    data = request.get_json() or {}
    plan = (data.get('plan') or '').strip().lower()

    if plan not in ('plata', 'oro', 'diamante'):
        return jsonify({'success': False, 'message': 'Plan inválido.'}), 400

    try:
        from app.factories.app_factory import db
        from app.utils.vip import aplicar_plan_vip, plan_ya_reclamado, PLANES_VIP
        from flask_login import login_user

        if plan_ya_reclamado(current_user.id_usuario, plan):
            nombre = PLANES_VIP[plan]['nombre']
            return jsonify({
                'success': False,
                'message': f'Ya activaste el {nombre}. Cada pase solo se reclama una vez.',
            }), 400

        plan_info, monedas = aplicar_plan_vip(current_user, plan)
        db.session.refresh(current_user)
        login_user(current_user)
        return jsonify({
            'success': True,
            'message': (
                f'¡{plan_info["nombre"]} activado! Recibiste {monedas} RiftCoins. '
                'Beneficios VIP activos en tu perfil.'
            ),
        })
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error procesando la activación.'}), 500

@jugador_bp.route('/perfil')
@login_required
def perfil():
    from app.factories.service_factory import get_service_factory
    from app.models.publicacion import Publicacion
    from sqlalchemy.orm import joinedload
    from app.models.comentario import Comentario

    sf = get_service_factory()
    usuario = sf.get_usuario_service().get_perfil(current_user.id_usuario)
    from app.utils.cosmetics import get_equipped_title_cosmetic
    titulo_tienda = get_equipped_title_cosmetic(usuario)
    publicaciones = (
        Publicacion.query.options(
            joinedload(Publicacion.autor),
            joinedload(Publicacion.usuarios_likes),
            joinedload(Publicacion.comentarios).joinedload(Comentario.autor),
            joinedload(Publicacion.reposteado).joinedload(Publicacion.autor),
        )
        .filter(Publicacion.id_usuario == current_user.id_usuario)
        .order_by(Publicacion.fecha_creacion.desc())
        .all()
    )
    return render_template(
        'jugador/perfil.html',
        usuario=usuario,
        titulo_tienda=titulo_tienda,
        publicaciones=publicaciones,
    )


@jugador_bp.route('/perfil/<username>')
@login_required
def perfil_publico(username):
    from app.factories.service_factory import get_service_factory
    from app.models.publicacion import Publicacion
    from sqlalchemy.orm import joinedload
    from app.models.comentario import Comentario

    sf = get_service_factory()
    user_service = sf.get_usuario_service()
    usuario = user_service.get_by_username(username)
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('jugador.dashboard'))
    from app.utils.cosmetics import get_equipped_title_cosmetic
    titulo_tienda = get_equipped_title_cosmetic(usuario)
    publicaciones = (
        Publicacion.query.options(
            joinedload(Publicacion.autor),
            joinedload(Publicacion.usuarios_likes),
            joinedload(Publicacion.comentarios).joinedload(Comentario.autor),
            joinedload(Publicacion.reposteado).joinedload(Publicacion.autor),
        )
        .filter(Publicacion.id_usuario == usuario.id_usuario)
        .order_by(Publicacion.fecha_creacion.desc())
        .all()
    )
    return render_template(
        'jugador/perfil.html',
        usuario=usuario,
        titulo_tienda=titulo_tienda,
        publicaciones=publicaciones,
    )


@jugador_bp.route('/publicacion/<int:post_id>')
@login_required
def ver_publicacion(post_id):
    from app.models.publicacion import Publicacion
    from app.models.comentario import Comentario
    from sqlalchemy.orm import joinedload

    post = Publicacion.query.options(
        joinedload(Publicacion.autor),
        joinedload(Publicacion.usuarios_likes),
        joinedload(Publicacion.comentarios).joinedload(Comentario.autor),
        joinedload(Publicacion.poll),
        joinedload(Publicacion.reposteado).joinedload(Publicacion.autor),
    ).get(post_id)

    if not post:
        flash('Publicación no encontrada.', 'error')
        return redirect(url_for('jugador.dashboard'))

    return render_template('jugador/publicacion_detalle.html', post=post)


@jugador_bp.route('/quitar-vip', methods=['POST'])
@login_required
def quitar_vip():
    from app.factories.app_factory import db
    from app.utils.vip import strip_vip
    from flask_login import login_user

    strip_vip(current_user)
    db.session.commit()
    login_user(current_user)
    flash('Membresía VIP eliminada de tu perfil.', 'success')
    return redirect(url_for('jugador.perfil'))

@jugador_bp.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if current_user.rol == 'invitado':
        flash('Los invitados no pueden editar su perfil. Crea una cuenta para acceder a esta función.', 'error')
        return redirect(url_for('auth.register'))
    if request.method == 'POST':
        from app.factories.service_factory import get_service_factory
        sf = get_service_factory()
        user_service = sf.get_usuario_service()
        
        # Procesamos los juegos favoritos como una cadena separada por comas
        juegos_seleccionados = request.form.getlist('juegos')
        juegos_str = ",".join(juegos_seleccionados) if juegos_seleccionados else ""
        
        from app.models.tienda import UserInventory, StoreItem
        from app.utils.cosmetics import titulo_desde_item

        titulo_form = request.form.get('titulo_perfil', 'Gamer')
        titulo_equipado_inv = (
            UserInventory.query.filter_by(user_id=current_user.id_usuario, is_equipped=True)
            .join(StoreItem)
            .filter(StoreItem.category == 'title')
            .first()
        )
        if titulo_equipado_inv:
            titulo_form = titulo_desde_item(titulo_equipado_inv.item.name)

        update_data = {
            'biografia': request.form.get('biografia', ''),
            'juegos_favoritos': juegos_str,
            'pais': request.form.get('pais', '').strip(),
            'disponibilidad': request.form.get('disponibilidad', '').strip(),
            'plataformas': request.form.get('plataformas', '').strip(),
            'estado_personalizado': request.form.get('estado_personalizado', '').strip(),
            'twitch': request.form.get('twitch', ''),
            'kick': request.form.get('kick', ''),
            'youtube': request.form.get('youtube', ''),
            'discord': request.form.get('discord', ''),
            'steam': request.form.get('steam', ''),
            'titulo_perfil': titulo_form,
        }
        
        if 'foto_perfil' in request.files:
            file = request.files['foto_perfil']
            if file and file.filename != '':
                from flask import current_app
                from app.utils.avatar import save_profile_photo

                nueva_foto = save_profile_photo(
                    file,
                    current_user.id_usuario,
                    current_app.config['UPLOAD_FOLDER'],
                )
                if not nueva_foto:
                    flash('Solo se permiten imágenes estáticas (PNG, JPG).', 'error')
                    return redirect(url_for('jugador.editar_perfil'))
                update_data['foto_perfil'] = nueva_foto

        if 'banner' in request.files:
            file = request.files['banner']
            if file and file.filename != '':
                from flask import current_app
                from app.utils.banner import save_banner_photo

                nuevo_banner = save_banner_photo(
                    file,
                    current_user.id_usuario,
                    current_app.config['UPLOAD_FOLDER'],
                )
                if not nuevo_banner:
                    flash('Solo se permiten imágenes estáticas para el banner (PNG, JPG).', 'error')
                    return redirect(url_for('jugador.editar_perfil'))
                update_data['banner'] = nuevo_banner

        usuario_actualizado = user_service.actualizar_perfil(
            current_user.id_usuario, **update_data
        )
        if usuario_actualizado:
            from app.factories.app_factory import db
            db.session.refresh(usuario_actualizado)
            login_user(usuario_actualizado, remember=True)
        flash('Perfil actualizado con éxito.', 'success')
        return redirect(url_for('jugador.perfil'))
        
    return render_template('jugador/editar_perfil.html')


@jugador_bp.route('/seguir/<int:user_id>', methods=['POST'])
@login_required
def seguir(user_id):
    from app.factories.service_factory import get_service_factory
    from flask import jsonify
    sf = get_service_factory()
    user_service = sf.get_usuario_service()
    objetivo = user_service.get_perfil(user_id)
    
    if not objetivo or objetivo.id_usuario == current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No puedes seguirte a ti mismo.'}), 400
    
    from app.factories.app_factory import db
    if current_user.esta_siguiendo(objetivo):
        current_user.dejar_de_seguir(objetivo)
        following = False
    else:
        current_user.seguir(objetivo)
        following = True
        
        # Generar Notificación
        notificacion_service = sf.get_notificacion_service()
        if notificacion_service:
            notificacion_service.crear_notificacion(
                usuario_id=objetivo.id_usuario,
                tipo='seguir',
                mensaje=f'¡{current_user.username} ha comenzado a seguirte!',
                enlace=url_for('jugador.perfil_publico', username=current_user.username)
            )
            
    db.session.commit()
    
    return jsonify({
        'success': True,
        'following': following,
        'seguidores_count': objetivo.num_seguidores
    })

@jugador_bp.route('/api/comunidad/seguir', methods=['POST'])
@login_required
def api_seguir_comunidad():
    from app.factories.app_factory import db
    from app.factories.service_factory import get_service_factory
    data = request.get_json(silent=True) or {}
    juego = data.get('juego', '').strip()
    if not juego:
        return jsonify({'success': False, 'message': 'Falta el nombre de la comunidad'}), 400
    siguiendo = not current_user.esta_siguiendo_comunidad(juego)
    if siguiendo:
        current_user.seguir_comunidad(juego)
        sf = get_service_factory()
        ns = sf.get_notificacion_service()
        ns.crear_notificacion(
            usuario_id=current_user.id_usuario,
            tipo='comunidad',
            mensaje=f'Has comenzado a seguir la comunidad {juego}',
            enlace=url_for('jugador.comunidad_detalle', juego=juego),
            icono='fas fa-gamepad',
        )
    else:
        current_user.dejar_seguir_comunidad(juego)
    db.session.commit()
    return jsonify({'success': True, 'following': siguiendo})

@jugador_bp.route('/comunidades')
@login_required
def comunidades():
    from app.data.game_categories import get_comunidades_categories
    from app.factories.app_factory import db
    from app.models.usuario import seguidores_comunidad
    categorias = get_comunidades_categories(url_for)
    siguiendo = set()
    if current_user.is_authenticated:
        rows = db.session.query(seguidores_comunidad.c.comunidad).filter(
            seguidores_comunidad.c.usuario_id == current_user.id_usuario
        ).all()
        siguiendo = {r[0] for r in rows}
    return render_template('jugador/comunidades.html',
                           categorias=categorias,
                           siguiendo_comunidades=siguiendo)

@jugador_bp.route('/notificaciones/leer')
@login_required
def leer_notificaciones():
    from app.factories.app_factory import db
    from app.models.usuario import Notificacion
    
    # Marcar todas como leídas
    notifs = current_user.notificaciones.filter_by(leido=False).all()
    for n in notifs:
        n.leido = True
    db.session.commit()
    
    from urllib.parse import urlparse
    ref = request.referrer
    if ref:
        parsed = urlparse(ref)
        if parsed.netloc and parsed.netloc != request.host:
            ref = None
    return redirect(ref or url_for('jugador.dashboard'))

@jugador_bp.route('/notificaciones')
@login_required
def notificaciones():
    from app.factories.app_factory import db
    from app.models.usuario import Notificacion
    
    page = request.args.get('page', 1, type=int)
    por_pagina = 30
    
    query = current_user.notificaciones
    pagination = db.paginate(query, page=page, per_page=por_pagina, error_out=False)
    
    notificaciones = pagination.items
    total = pagination.total
    
    return render_template(
        'jugador/notificaciones.html',
        notificaciones=notificaciones,
        pagination=pagination,
        total=total
    )

@jugador_bp.route('/comunidad/<juego>')
@login_required
def comunidad_detalle(juego):
    from app.factories.app_factory import db
    from app.models.publicacion import Publicacion, Poll, PollOption
    from app.models.comentario import Comentario
    from sqlalchemy.orm import joinedload
    from app.factories.service_factory import get_service_factory
    from app.data.game_categories import get_game_categories
    
    tab = request.args.get('tab', 'para-ti')
    valid_tabs = ('para-ti', 'siguiendo', 'tendencias', 'videos', 'encuestas', 'recientes')
    if tab not in valid_tabs:
        tab = 'para-ti'
    
    base_query = Publicacion.query.options(
        joinedload(Publicacion.autor),
        joinedload(Publicacion.usuarios_likes),
        joinedload(Publicacion.comentarios).joinedload(Comentario.autor),
        joinedload(Publicacion.poll).joinedload(Poll.options),
        joinedload(Publicacion.reposteado).joinedload(Publicacion.autor),
    ).filter(Publicacion.juego == juego)
    
    if tab == 'videos':
        base_query = base_query.filter(
            db.or_(Publicacion.video_archivo.isnot(None), Publicacion.video_archivo != '')
        ).order_by(Publicacion.promocionada.desc(), Publicacion.fecha_creacion.desc())
    elif tab == 'encuestas':
        base_query = base_query.filter(Publicacion.poll.has()).order_by(Publicacion.promocionada.desc(), Publicacion.fecha_creacion.desc())
    elif tab == 'siguiendo':
        follow_ids = [f.id_usuario_sigue for f in current_user.seguidos]
        follow_ids.append(current_user.id_usuario)
        base_query = base_query.filter(Publicacion.id_usuario.in_(follow_ids)).order_by(Publicacion.promocionada.desc(), Publicacion.fecha_creacion.desc())
    elif tab == 'tendencias':
        base_query = base_query.order_by(Publicacion.promocionada.desc(), Publicacion.shares_count.desc(), Publicacion.likes_count.desc())
    elif tab == 'recientes':
        base_query = base_query.order_by(Publicacion.promocionada.desc(), Publicacion.fecha_creacion.desc())
    else:
        base_query = base_query.order_by(Publicacion.promocionada.desc(), Publicacion.fecha_creacion.desc())
    
    publicaciones = base_query.limit(50).all()
    
    # Find category color for this game
    color = '#8b5cf6'
    for cat in get_game_categories():
        for g in cat['juegos']:
            if g['nombre'].lower() == juego.lower():
                color = cat['color']
                break
        else:
            continue
        break
    
    # Build a flat list of all communities for repost target
    todas_comunidades = []
    for cat in get_game_categories():
        for g in cat['juegos']:
            todas_comunidades.append({'nombre': g['nombre'], 'color': cat['color']})
    
    siguiendo = current_user.esta_siguiendo_comunidad(juego) if current_user.is_authenticated else False

    return render_template('jugador/comunidad_detalle.html',
        juego=juego, publicaciones=publicaciones, color=color,
        active_tab=tab, todas_comunidades=todas_comunidades,
        siguiendo=siguiendo)


@jugador_bp.route('/videos')
@login_required
def videos():
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    videos = pub_service.obtener_videos(user_id=current_user.id_usuario)
    return render_template('dashboard/videos/videos.html', videos=videos)


@jugador_bp.route('/subir-clip', methods=['GET', 'POST'])
@login_required
def subir_clip():
    import uuid, os

    if request.method == 'GET':
        return render_template('jugador/subir_clip.html')

    if 'video' not in request.files:
        return jsonify({'success': False, 'message': 'No se envió ningún archivo.'}), 400

    file = request.files['video']
    if not file.filename:
        return jsonify({'success': False, 'message': 'Archivo vacío.'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    allowed = current_app.config.get('ALLOWED_VIDEO_EXTENSIONS', {'mp4', 'mov', 'avi'})
    if ext not in allowed:
        return jsonify({'success': False, 'message': 'Formato no permitido. Solo .mp4, .mov, .avi.'}), 400

    if not file.content_type or not file.content_type.startswith('video/'):
        return jsonify({'success': False, 'message': 'El archivo no es un video válido.'}), 400

    filename = f'clip_{uuid.uuid4().hex[:16]}.{ext}'
    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'videos')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))

    video_url = url_for('static', filename=f'uploads/videos/{filename}')

    flash('¡Clip subido correctamente!', 'success')
    return jsonify({'success': True, 'video_url': video_url})


@jugador_bp.route('/eliminar-publicacion/<int:post_id>', methods=['POST'])
@login_required
def eliminar_publicacion(post_id):
    from app.factories.app_factory import db
    from app.models.publicacion import Publicacion
    post = Publicacion.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'Publicación no encontrada.'}), 404
    if post.id_usuario != current_user.id_usuario and current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403
    db.session.delete(post)
    db.session.commit()
    flash('Publicación eliminada.', 'success')
    return jsonify({'success': True})


@jugador_bp.route('/editar-publicacion/<int:post_id>', methods=['POST'])
@login_required
def editar_publicacion(post_id):
    from app.factories.app_factory import db
    from app.models.publicacion import Publicacion
    from app.utils.profanity import filter_profanity
    post = Publicacion.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'Publicación no encontrada.'}), 404
    if post.id_usuario != current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403
    data = request.get_json(silent=True) or {}
    contenido = data.get('contenido', '').strip()
    if not contenido:
        return jsonify({'success': False, 'message': 'El contenido no puede estar vacío.'}), 400
    post.contenido = filter_profanity(contenido)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Publicación actualizada.', 'contenido': post.contenido})


@jugador_bp.route('/fijar-publicacion/<int:post_id>', methods=['POST'])
@login_required
def fijar_publicacion(post_id):
    from app.factories.app_factory import db
    from app.models.publicacion import Publicacion
    post = Publicacion.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'Publicación no encontrada.'}), 404
    if post.id_usuario != current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403
    post.fijada = not post.fijada
    db.session.commit()
    estado = 'fijada' if post.fijada else 'desfijada'
    flash(f'Publicación {estado}.', 'success')
    return jsonify({'success': True, 'fijada': post.fijada})


@jugador_bp.route('/reportar-publicacion/<int:post_id>', methods=['POST'])
@login_required
def reportar_publicacion(post_id):
    from app.factories.app_factory import db
    from app.models.publicacion import Report
    data = request.get_json() or {}
    motivo = data.get('motivo', 'spam')
    if motivo not in ('spam', 'contenido_inapropiado', 'acoso', 'otro'):
        motivo = 'spam'
    reporte = Report(
        id_publicacion=post_id,
        id_usuario=current_user.id_usuario,
        motivo=motivo,
        descripcion=data.get('descripcion', ''),
    )
    db.session.add(reporte)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Reporte enviado. Lo revisaremos pronto.'})


@jugador_bp.route('/ocultar-publicacion/<int:post_id>', methods=['POST'])
@login_required
def ocultar_publicacion(post_id):
    from app.factories.app_factory import db
    from app.models.publicacion import publicacion_oculta
    conn = db.engine.connect()
    conn.execute(publicacion_oculta.insert().values(id_usuario=current_user.id_usuario, id_publicacion=post_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@jugador_bp.route('/api/notificaciones', methods=['GET'])
@login_required
def api_notificaciones():
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    ns = sf.get_notificacion_service()
    notifs = ns.obtener_notificaciones(current_user.id_usuario)
    return jsonify({
        'success': True,
        'no_leidas': ns.no_leidas_count(current_user.id_usuario),
        'notificaciones': [{
            'id': n.id_notificacion,
            'tipo': n.tipo,
            'mensaje': n.mensaje,
            'enlace': n.enlace,
            'icono': n.icono,
            'leido': n.leido,
            'fecha': n.fecha_creacion.isoformat() if n.fecha_creacion else None,
        } for n in notifs],
    })


@jugador_bp.route('/api/notificaciones/leer', methods=['POST'])
@login_required
def api_notificaciones_leer():
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    ns = sf.get_notificacion_service()
    ns.marcar_leidas(current_user.id_usuario)
    return jsonify({'success': True})


@jugador_bp.route('/api/notificaciones/contar', methods=['GET'])
@login_required
def api_notificaciones_contar():
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    ns = sf.get_notificacion_service()
    return jsonify({'no_leidas': ns.no_leidas_count(current_user.id_usuario)})
