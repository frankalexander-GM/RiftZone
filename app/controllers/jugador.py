from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user, login_user

jugador_bp = Blueprint('jugador', __name__, template_folder='../templates/jugador')

@jugador_bp.route('/dashboard')
@login_required
def dashboard():
    tab = request.args.get('tab', 'para-ti')
    if tab not in ('para-ti', 'siguiendo', 'populares', 'recientes', 'encuestas', 'torneos'):
        tab = 'para-ti'
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    publicaciones = pub_service.obtener_feed(tab=tab, user_id=current_user.id_usuario)
    return render_template('jugador/dashboard.html', publicaciones=publicaciones, active_tab=tab)

@jugador_bp.route('/explorar')
def explorar():
    from app.factories.service_factory import get_service_factory
    from app.models.usuario import Usuario
    from app.models.clan import Clan
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    user_id = current_user.id_usuario if current_user.is_authenticated else None
    publicaciones = pub_service.obtener_feed(user_id=user_id)
    usuarios = Usuario.query.order_by(Usuario.nivel.desc()).limit(12).all()
    clanes = Clan.query.order_by(Clan.fecha_creacion.desc()).limit(6).all()
    return render_template('jugador/explorar.html', publicaciones=publicaciones, usuarios=usuarios, clanes=clanes)

@jugador_bp.route('/crear-publicacion', methods=['POST'])
@login_required
def crear_publicacion():
    from app.factories.service_factory import get_service_factory
    from app.factories.app_factory import db
    from flask import current_app
    from app.models.publicacion import Poll, PollOption
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    
    contenido = request.form.get('contenido', '').strip()
    juego = request.form.get('juego')
    tipo_post = request.form.get('tipo_post', 'texto')
    imagen_url = request.form.get('imagen_url', '').strip()
    imagen_archivo = request.files.get('imagen_archivo')
    video_archivo = request.files.get('video_archivo')
    clip_url = request.form.get('clip_url', '').strip()

    def _save_upload(file, subdir='images'):
        import os, uuid
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
        filename = f'post_{uuid.uuid4().hex[:12]}.{ext}'
        upload_dir = os.path.join(current_app.static_folder, 'uploads', subdir)
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        return url_for('static', filename=f'uploads/{subdir}/{filename}')

    # File upload priority: video_archivo > imagen_archivo > imagen_url > clip_url
    if video_archivo and video_archivo.filename:
        ext = video_archivo.filename.rsplit('.', 1)[-1].lower() if '.' in video_archivo.filename else ''
        if ext not in ('mp4', 'mov', 'avi') or not video_archivo.content_type.startswith('video/'):
            flash('El archivo no es un video válido (solo .mp4, .mov, .avi).', 'error')
            return redirect(url_for('jugador.dashboard'))
        imagen_url = _save_upload(video_archivo, 'videos')
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
        if clip_url and not imagen_url:
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
    
    elif tipo_post == 'tournament':
        nombre = request.form.get('tour_nombre', '').strip()
        fecha = request.form.get('tour_fecha', '').strip()
        hora = request.form.get('tour_hora', '').strip()
        cupos = request.form.get('tour_cupos', '').strip()
        premio = request.form.get('tour_premio', '').strip()
        tour_juego = request.form.get('tour_juego', '').strip()
        formato = request.form.get('tour_formato', '').strip()
        desc = request.form.get('tour_desc', '').strip()
        partes = []
        if nombre: partes.append(f'🏆 {nombre}')
        if fecha: partes.append(f'📅 {fecha}{(" " + hora) if hora else ""}')
        if cupos: partes.append(f'👥 {cupos} cupos')
        if premio: partes.append(f'💰 {premio}')
        if formato: partes.append(f'⚔ {formato}')
        if tour_juego: partes.append(f'🎮 {tour_juego}')
        if desc: partes.append(f'📝 {desc}')
        if partes:
            contenido = '[Torneo] ' + ' | '.join(partes)
        if tour_juego and not juego:
            juego = tour_juego
    
    try:
        post = pub_service.crear_publicacion(
            id_usuario=current_user.id_usuario,
            contenido=contenido or 'Publicación',
            juego=juego,
            imagen_url=imagen_url or None
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

    sf = get_service_factory()
    com_service = sf.get_comentario_service()
    contenido = (request.form.get('contenido') or '').strip()
    if not contenido and request.is_json:
        contenido = (request.get_json(silent=True) or {}).get('contenido', '').strip()

    try:
        com = com_service.crear_comentario(
            id_publicacion=post_id,
            id_usuario=current_user.id_usuario,
            contenido=contenido,
        )
        comments_count = Comentario.query.filter_by(id_publicacion=post_id).count()

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
        return jsonify({'success': True, 'liked': liked, 'likes_count': likes_count})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception:
        from app.factories.app_factory import db
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al procesar el like.'}), 500

@jugador_bp.route('/promocionar/<int:post_id>', methods=['POST'])
@login_required
def promocionar(post_id):
    flash('Elige un plan de boost en la Central de Boosts.', 'success')
    return redirect(url_for('jugador.boosts', post_id=post_id))

@jugador_bp.route('/boosts')
@login_required
def boosts():
    from app.models.publicacion import Publicacion
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

    return render_template(
        'jugador/boosts.html',
        post_target=post,
        mis_posts=mis_posts,
        boost_planes=BOOST_PLANS,
        saldo=current_user.tokens or 0,
    )


@jugador_bp.route('/comprar-boost', methods=['POST'])
@login_required
def comprar_boost():
    if current_user.rol == 'invitado':
        flash('Regístrate para usar boosts.', 'error')
        return redirect(url_for('jugador.boosts'))

    plan = (request.form.get('plan') or '').strip()
    post_id = request.form.get('post_id', type=int)

    if not post_id:
        flash('Selecciona una publicación para boostear.', 'error')
        return redirect(url_for('jugador.boosts'))

    try:
        from app.services.boost_service import aplicar_boost
        from flask_login import login_user
        from app.factories.app_factory import db

        post, plan_info = aplicar_boost(current_user, post_id, plan)
        db.session.refresh(current_user)
        login_user(current_user)
        etiquetas = {'rapido': 'azul', 'mega': 'morado', 'titan': 'dorado'}
        color_txt = etiquetas.get(plan, '')
        flash(
            f'¡{plan_info["nombre"]} activado! Tu nombre se verá en {color_txt} en el perfil y en el chat. '
            f'Saldo: {current_user.tokens} RC.',
            'success',
        )
        return redirect(url_for('jugador.dashboard'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('jugador.boosts', post_id=post_id))
    except Exception:
        from app.factories.app_factory import db
        db.session.rollback()
        flash('Error al aplicar el boost.', 'error')
        return redirect(url_for('jugador.boosts', post_id=post_id))

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

@jugador_bp.route('/comunidades')
@login_required
def comunidades():
    categorias = [
        {
            "titulo": "🔫 Fuerza Élite",
            "descripcion": "Shooters tácticos, precisión y reflejos. La cima del combate competitivo.",
            "juegos": [
                {"nombre": "Counter-Strike 2", "imagen": url_for('static', filename='img/comunidades/shooters/cs2.jpg'), "desc": "Rey de Steam, rompe récords de jugadores simultáneos."},
                {"nombre": "Valorant", "imagen": url_for('static', filename='img/comunidades/shooters/valorant.jpg'), "desc": "Shooter competitivo con comunidad enorme."},
                {"nombre": "Rainbow Six Siege", "imagen": url_for('static', filename='img/comunidades/shooters/rainbow6.jpg'), "desc": "Competitivo táctico mantiene su comunidad."},
                {"nombre": "Overwatch 2", "imagen": url_for('static', filename='img/comunidades/shooters/overwatch2.jpg'), "desc": "Héroes, acción rápida y comunidad global."},
                {"nombre": "The Finals", "imagen": url_for('static', filename='img/comunidades/shooters/thefinals.jpg'), "desc": "Free-to-play que sigue creciendo."},
                {"nombre": "Destiny 2", "imagen": url_for('static', filename='img/comunidades/shooters/destiny2.jpg'), "desc": "Expansiones constantes y modelo live service."},
                {"nombre": "Call of Duty: Black Ops 6", "imagen": url_for('static', filename='img/comunidades/shooters/bo6.jpg'), "desc": "El shooter anual más esperado."},
                {"nombre": "Team Fortress 2", "imagen": url_for('static', filename='img/comunidades/shooters/tf2.jpg'), "desc": "Clásico de Valve con legión de seguidores."},
                {"nombre": "Battlefield 2042", "imagen": url_for('static', filename='img/comunidades/shooters/bf2042.jpg'), "desc": "Combate a gran escala con vehículos y destrucción."},
                {"nombre": "Escape from Tarkov", "imagen": url_for('static', filename='img/comunidades/shooters/tarkov.jpg'), "desc": "Shooter hardcore de extracción."},
                {"nombre": "Hunt: Showdown", "imagen": url_for('static', filename='img/comunidades/shooters/hunt.jpg'), "desc": "Caza de monstruos con ambiente western."},
                {"nombre": "Splitgate", "imagen": url_for('static', filename='img/comunidades/shooters/splitgate.jpg'), "desc": "Halo + Portal. Acción con portales."},
                {"nombre": "XDefiant", "imagen": url_for('static', filename='img/comunidades/shooters/xdefiant.jpg'), "desc": "Shooter arcade de Ubisoft con facciones."},
            ]
        },
        {
            "titulo": "🏆 Reyes de la Batalla",
            "descripcion": "Battle royales masivos. Último en pie, gloria eterna.",
            "juegos": [
                {"nombre": "Fortnite", "imagen": url_for('static', filename='img/comunidades/shooters/fortnite.jpg'), "desc": "Eventos constantes, colaboraciones y nuevos modos."},
                {"nombre": "Call of Duty: Warzone", "imagen": url_for('static', filename='img/comunidades/shooters/warzone.jpg'), "desc": "Battle royale masivo de Activision."},
                {"nombre": "Apex Legends", "imagen": url_for('static', filename='img/comunidades/shooters/apex.jpg'), "desc": "Acción rápida y temporadas constantes."},
                {"nombre": "PUBG: Battlegrounds", "imagen": url_for('static', filename='img/comunidades/shooters/pubg.jpg'), "desc": "El pionero del género battle royale."},
                {"nombre": "Free Fire", "imagen": url_for('static', filename='img/comunidades/shooters/freefire.jpg'), "desc": "El rey de los battle royale para móviles."},
                {"nombre": "Fall Guys", "imagen": url_for('static', filename='img/comunidades/shooters/fallguys.jpg'), "desc": "Battle royale de obstáculos y locura."},
                {"nombre": "Call of Duty Mobile", "imagen": url_for('static', filename='img/comunidades/shooters/codm.jpg'), "desc": "La experiencia CoD en tu celular."},
                {"nombre": "Stumble Guys", "imagen": url_for('static', filename='img/comunidades/shooters/stumble.jpg'), "desc": "Party battle royale con millones de descargas."},
            ]
        },
        {
            "titulo": "🧙‍♂️ Tripulación Legendaria",
            "descripcion": "MOBA, RPG, MMO y acción. Leyendas que forjan su destino.",
            "juegos": [
                {"nombre": "League of Legends", "imagen": url_for('static', filename='img/comunidades/shooters/lol.jpg'), "desc": "El MOBA más grande del planeta."},
                {"nombre": "Dota 2", "imagen": url_for('static', filename='img/comunidades/mobas/dota2.jpg'), "desc": "Clásico que sigue dominando Steam."},
                {"nombre": "Mobile Legends: Bang Bang", "imagen": url_for('static', filename='img/comunidades/shooters/mlbb.jpg'), "desc": "El MOBA definitivo para dispositivos móviles."},
                {"nombre": "Honor of Kings", "imagen": url_for('static', filename='img/comunidades/shooters/hok.jpg'), "desc": "El MOBA más jugado del mundo."},
                {"nombre": "Genshin Impact", "imagen": url_for('static', filename='img/comunidades/shooters/genshin.jpg'), "desc": "RPG gacha de mundo abierto."},
                {"nombre": "Warframe", "imagen": url_for('static', filename='img/comunidades/shooters/warframe.jpg'), "desc": "Una de las comunidades más fieles."},
                {"nombre": "World of Warcraft", "imagen": url_for('static', filename='img/comunidades/shooters/wow.jpg'), "desc": "El MMO por excelencia."},
                {"nombre": "Final Fantasy XIV", "imagen": url_for('static', filename='img/comunidades/shooters/ffxiv.jpg'), "desc": "MMORPG con historia épica."},
                {"nombre": "Baldur's Gate 3", "imagen": url_for('static', filename='img/comunidades/shooters/bg3.jpg'), "desc": "RPG del año con comunidad gigante."},
                {"nombre": "Diablo IV", "imagen": url_for('static', filename='img/comunidades/shooters/d4.jpg'), "desc": "Action RPG oscuro y adictivo."},
                {"nombre": "Path of Exile", "imagen": url_for('static', filename='img/comunidades/shooters/poe.jpg'), "desc": "El ARPG más profundo y gratuito."},
                {"nombre": "Lost Ark", "imagen": url_for('static', filename='img/comunidades/shooters/lostark.jpg'), "desc": "MMOARPG con combate espectacular."},
                {"nombre": "Black Desert Online", "imagen": url_for('static', filename='img/comunidades/shooters/bdo.jpg'), "desc": "MMO sandbox con combate fluido."},
                {"nombre": "Elden Ring", "imagen": url_for('static', filename='img/comunidades/shooters/eldenring.jpg'), "desc": "El fenómeno soulslike de mundo abierto."},
            ]
        },
        {
            "titulo": "🌍 Constructores de Mundos",
            "descripcion": "Sandbox, supervivencia y libertad total. Crea tu propia historia.",
            "juegos": [
                {"nombre": "Minecraft", "imagen": url_for('static', filename='img/comunidades/shooters/minecraft.jpg'), "desc": "Fenómeno eterno con millones de jugadores diarios."},
                {"nombre": "Roblox", "imagen": url_for('static', filename='img/comunidades/shooters/roblox.jpg'), "desc": "Plataforma con cifras gigantes de jugadores."},
                {"nombre": "GTA V / GTA Online", "imagen": url_for('static', filename='img/comunidades/supervivencia/gtav.jpg'), "desc": "Impulsado por el hype de GTA VI."},
                {"nombre": "Palworld", "imagen": url_for('static', filename='img/comunidades/shooters/palworld.jpg'), "desc": "Pokémon con armas que conquistó el mundo."},
                {"nombre": "ARK: Survival Evolved", "imagen": url_for('static', filename='img/comunidades/shooters/ark.jpg'), "desc": "Dinosaurios, supervivencia y construcción épica."},
                {"nombre": "Rust", "imagen": url_for('static', filename='img/comunidades/shooters/rust.jpg'), "desc": "Supervivencia hardcore con comunidad intensa."},
                {"nombre": "Terraria", "imagen": url_for('static', filename='img/comunidades/shooters/terraria.jpg'), "desc": "Sandbox 2D con contenido infinito."},
                {"nombre": "Valheim", "imagen": url_for('static', filename='img/comunidades/shooters/valheim.jpg'), "desc": "Supervivencia vikinga que enamoró a todos."},
                {"nombre": "No Man's Sky", "imagen": url_for('static', filename='img/comunidades/shooters/nms.jpg'), "desc": "Exploración espacial sin límites."},
                {"nombre": "Red Dead Redemption 2", "imagen": url_for('static', filename='img/comunidades/shooters/rdr2.jpg'), "desc": "El oeste salvaje con el mejor mundo abierto."},
                {"nombre": "Cyberpunk 2077", "imagen": url_for('static', filename='img/comunidades/shooters/cyberpunk.jpg'), "desc": "RPG futurista con comunidad enorme."},
                {"nombre": "Sea of Thieves", "imagen": url_for('static', filename='img/comunidades/shooters/sot.jpg'), "desc": "Aventuras pirata cooperativas."},
                {"nombre": "The Forest", "imagen": url_for('static', filename='img/comunidades/shooters/forest.jpg'), "desc": "Supervivencia y terror en una isla."},
            ]
        },
        {
            "titulo": "🎯 Fiebre Global",
            "descripcion": "Deportes, party games y cooperativo. Diversión para todos.",
            "juegos": [
                {"nombre": "EA Sports FC 26", "imagen": url_for('static', filename='img/comunidades/shooters/eafc26.jpg'), "desc": "El fútbol sigue siendo de lo más jugado."},
                {"nombre": "Rocket League", "imagen": url_for('static', filename='img/comunidades/shooters/rocket.jpg'), "desc": "Fútbol con coches. Simple y adictivo."},
                {"nombre": "Helldivers 2", "imagen": url_for('static', filename='img/comunidades/shooters/helldivers2.jpg'), "desc": "Cooperativo con picos masivos de jugadores."},
                {"nombre": "Among Us", "imagen": url_for('static', filename='img/comunidades/shooters/amongus.jpg'), "desc": "El party game que nunca muere."},
                {"nombre": "Dead by Daylight", "imagen": url_for('static', filename='img/comunidades/shooters/dbd.jpg'), "desc": "Asimétrico de terror. Comunidad enorme."},
                {"nombre": "Phasmophobia", "imagen": url_for('static', filename='img/comunidades/shooters/phasmo.jpg'), "desc": "Caza fantasmas cooperativa."},
                {"nombre": "Lethal Company", "imagen": url_for('static', filename='img/comunidades/shooters/lethal.jpg'), "desc": "Cooperativo de terror que explotó en Twitch."},
                {"nombre": "Brawlhalla", "imagen": url_for('static', filename='img/comunidades/shooters/brawlhalla.jpg'), "desc": "Plataformas de lucha gratuito."},
                {"nombre": "Street Fighter 6", "imagen": url_for('static', filename='img/comunidades/shooters/sf6.jpg'), "desc": "El rey de los fighting games."},
                {"nombre": "Tekken 8", "imagen": url_for('static', filename='img/comunidades/shooters/tekken8.jpg'), "desc": "Peleas 3D con comunidad competitiva."},
                {"nombre": "Mario Kart 8 Deluxe", "imagen": url_for('static', filename='img/comunidades/shooters/mk8.jpg'), "desc": "Carreras arcade multijugador."},
                {"nombre": "Gran Turismo 7", "imagen": url_for('static', filename='img/comunidades/shooters/gt7.jpg'), "desc": "El simulador de carreras definitivo."},
                {"nombre": "Forza Horizon 5", "imagen": url_for('static', filename='img/comunidades/shooters/fh5.jpg'), "desc": "Mundo abierto sobre ruedas."},
            ]
        },
    ]
    return render_template('jugador/comunidades.html', 
                           categorias=categorias)

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
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    
    # Obtenemos todas y filtramos por el juego seleccionado
    todas_publicaciones = pub_service.obtener_feed(user_id=current_user.id_usuario)
    publicaciones_juego = [p for p in todas_publicaciones if p.juego == juego]
    
    return render_template('jugador/comunidad_detalle.html', juego=juego, publicaciones=publicaciones_juego)


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


@jugador_bp.route('/sugerir_juego', methods=['POST'])
@login_required
def sugerir_juego():
    from app.factories.app_factory import db
    from app.models.usuario import Sugerencia
    juego = request.form.get('juego', '').strip()
    if not juego:
        flash('Escribe el nombre del juego que quieres sugerir.', 'error')
        return redirect(url_for('jugador.comunidades'))
    if len(juego) > 200:
        flash('El nombre es muy largo (máx 200 caracteres).', 'error')
        return redirect(url_for('jugador.comunidades'))
    sugerencia = Sugerencia(usuario_id=current_user.id_usuario, juego_nombre=juego)
    db.session.add(sugerencia)
    db.session.commit()
    flash(f'Gracias por sugerir "{juego}" — lo revisaremos pronto.', 'success')
    return redirect(url_for('jugador.comunidades'))



