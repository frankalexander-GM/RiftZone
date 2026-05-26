from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user

jugador_bp = Blueprint('jugador', __name__, template_folder='../templates/jugador')

@jugador_bp.route('/dashboard')
@login_required
def dashboard():
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    publicaciones = pub_service.obtener_feed()
    return render_template('jugador/dashboard.html', publicaciones=publicaciones)

@jugador_bp.route('/explorar')
def explorar():
    from app.factories.service_factory import get_service_factory
    from app.models.usuario import Usuario
    from app.models.clan import Clan
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    publicaciones = pub_service.obtener_feed()
    usuarios = Usuario.query.order_by(Usuario.nivel.desc()).limit(12).all()
    clanes = Clan.query.order_by(Clan.fecha_creacion.desc()).limit(6).all()
    return render_template('jugador/explorar.html', publicaciones=publicaciones, usuarios=usuarios, clanes=clanes)

@jugador_bp.route('/crear-publicacion', methods=['POST'])
@login_required
def crear_publicacion():
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    
    contenido = request.form.get('contenido')
    juego = request.form.get('juego')
    imagen_url = request.form.get('imagen_url')
    
    try:
        pub_service.crear_publicacion(
            id_usuario=current_user.id_usuario,
            contenido=contenido,
            juego=juego,
            imagen_url=imagen_url
        )
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

    sf = get_service_factory()
    usuario = sf.get_usuario_service().get_perfil(current_user.id_usuario)
    from app.utils.cosmetics import get_equipped_title_cosmetic
    titulo_tienda = get_equipped_title_cosmetic(usuario)
    return render_template(
        'jugador/perfil.html',
        usuario=usuario,
        titulo_tienda=titulo_tienda,
    )


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

@jugador_bp.route('/perfil/<username>')
@login_required
def perfil_publico(username):
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    user_service = sf.get_usuario_service()
    usuario = user_service.get_by_username(username)
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('jugador.dashboard'))
    from app.utils.cosmetics import get_equipped_title_cosmetic
    titulo_tienda = get_equipped_title_cosmetic(usuario)
    return render_template(
        'jugador/perfil.html',
        usuario=usuario,
        titulo_tienda=titulo_tienda,
    )

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
            "titulo": "🔥 Los Titanes Mundiales",
            "descripcion": "Los juegos más populares y jugados a nivel global. El top absoluto.",
            "carpeta": "titanes",
            "juegos": [
                {"nombre": "Roblox", "imagen": url_for('static', filename='img/comunidades/titanes/roblox.jpg'), "desc": "Imaginación sin límites en millones de mundos."},
                {"nombre": "Counter-Strike 2", "imagen": url_for('static', filename='img/comunidades/titanes/cs2.jpg'), "desc": "El shooter táctico por excelencia, ahora renovado."},
                {"nombre": "Minecraft", "imagen": url_for('static', filename='img/comunidades/titanes/minecraft.jpg'), "desc": "Exploración, construcción y supervivencia infinita."},
                {"nombre": "EA SPORTS FC 26", "imagen": url_for('static', filename='img/comunidades/titanes/eafc26.jpg'), "desc": "El juego del mundo. Fútbol en su máxima expresión."}
            ]
        },
        {
            "titulo": "🎯 Shooters y Battle Royales",
            "descripcion": "Competencia pura. Apunta, dispara y sé el último en pie.",
            "carpeta": "shooters",
            "juegos": [
                {"nombre": "Call of Duty: Warzone", "imagen": url_for('static', filename='img/comunidades/shooters/warzone.jpg'), "desc": "Battle Royale intenso y táctico en el universo CoD."},
                {"nombre": "Apex Legends", "imagen": url_for('static', filename='img/comunidades/shooters/apex.jpg'), "desc": "Shooter de héroes rápido y dinámico."},
                {"nombre": "Valorant", "imagen": url_for('static', filename='img/comunidades/shooters/valorant.jpg'), "desc": "Shooter táctico 5v5 de Riot Games. Precisión pura."},
                {"nombre": "Fortnite", "imagen": url_for('static', filename='img/comunidades/shooters/fortnite.jpg'), "desc": "Construye, sobrevive y compite en el metaverso."},
                {"nombre": "Free Fire", "imagen": url_for('static', filename='img/comunidades/shooters/freefire.jpg'), "desc": "El rey de los Battle Royale para móviles."},
                {"nombre": "Overwatch 2", "imagen": url_for('static', filename='img/comunidades/shooters/overwatch2.jpg'), "desc": "Trabajo en equipo y héroes únicos."}
            ]
        },
        {
            "titulo": "⚔️ Gigantes Tácticos y MOBA",
            "descripcion": "Estrategia en tiempo real. Trabaja en equipo para destruir el nexo rival.",
            "carpeta": "mobas",
            "juegos": [
                {"nombre": "Honor of Kings", "imagen": url_for('static', filename='img/comunidades/mobas/honor of kings.jpg'), "desc": "El MOBA táctico de batallas épicas 5v5."},
                {"nombre": "Mobile Legends: Bang Bang", "imagen": url_for('static', filename='img/comunidades/mobas/mobilelegends.jpg'), "desc": "El MOBA definitivo para dispositivos móviles."},
                {"nombre": "Dota 2", "imagen": url_for('static', filename='img/comunidades/mobas/dota2.jpg'), "desc": "Complejo, profundo y enormemente gratificante."}
            ]
        },
        {
            "titulo": "🌲 Supervivencia y Mundo Abierto",
            "descripcion": "Explora mundos gigantescos, sobrevive y crea tu propia historia.",
            "carpeta": "supervivencia",
            "juegos": [
                {"nombre": "ARK: Survival Evolved", "imagen": url_for('static', filename='img/comunidades/supervivencia/ark.jpg'), "desc": "Dinosaurios, supervivencia y construcción épica."},
                {"nombre": "GTA V / GTA Online", "imagen": url_for('static', filename='img/comunidades/supervivencia/gtav.jpg'), "desc": "Caos en mundo abierto, atracos y rol."}
            ]
        }
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

@jugador_bp.route('/comunidad/<juego>')
@login_required
def comunidad_detalle(juego):
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    
    # Obtenemos todas y filtramos por el juego seleccionado
    todas_publicaciones = pub_service.obtener_feed()
    publicaciones_juego = [p for p in todas_publicaciones if p.juego == juego]
    
    return render_template('jugador/comunidad_detalle.html', juego=juego, publicaciones=publicaciones_juego)



