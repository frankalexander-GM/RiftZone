from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

jugador_bp = Blueprint('jugador', __name__, template_folder='../templates/jugador')

@jugador_bp.route('/dashboard')
@login_required
def dashboard():
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    publicaciones = pub_service.obtener_feed()
    return render_template('jugador/dashboard.html', publicaciones=publicaciones)

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

@jugador_bp.route('/comentar/<int:post_id>', methods=['POST'])
@login_required
def comentar(post_id):
    from app.factories.service_factory import get_service_factory
    sf = get_service_factory()
    com_service = sf.get_comentario_service()
    
    contenido = request.form.get('contenido')
    try:
        com_service.crear_comentario(
            id_publicacion=post_id,
            id_usuario=current_user.id_usuario,
            contenido=contenido
        )
    except ValueError as e:
        flash(str(e), 'error')
        
        
    return redirect(request.referrer or url_for('jugador.dashboard'))

@jugador_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    from app.factories.service_factory import get_service_factory
    from flask import jsonify
    sf = get_service_factory()
    pub_service = sf.get_publicacion_service()
    
    try:
        liked = pub_service.toggle_like(post_id, current_user)
        post = pub_service.pub_repo.get_by_id(post_id)
        return jsonify({'success': True, 'liked': liked, 'likes_count': post.likes})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@jugador_bp.route('/perfil')
@login_required
def perfil():
    return render_template('jugador/perfil.html', usuario=current_user)

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
        
        user_service.actualizar_perfil(
            current_user.id_usuario,
            biografia=request.form.get('biografia', ''),
            foto_perfil=request.form.get('foto_perfil', ''),
            banner=request.form.get('banner', ''),
            juegos_favoritos=juegos_str,
            pais=request.form.get('pais', ''),
            estado_personalizado=request.form.get('estado_personalizado', ''),
            twitch=request.form.get('twitch', ''),
            kick=request.form.get('kick', ''),
            youtube=request.form.get('youtube', ''),
            discord=request.form.get('discord', ''),
            steam=request.form.get('steam', ''),
            titulo_perfil=request.form.get('titulo_perfil', 'Gamer')
        )
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
    return render_template('jugador/perfil.html', usuario=usuario)

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
                titulo='Nuevo Seguidor',
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
    
    return redirect(request.referrer or url_for('jugador.dashboard'))

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


