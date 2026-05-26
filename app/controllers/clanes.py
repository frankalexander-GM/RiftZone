from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.factories.service_factory import get_service_factory

clanes_bp = Blueprint('clanes', __name__, template_folder='../templates/jugador')

@clanes_bp.route('/')
def index():
    sf = get_service_factory()
    clan_service = sf.get_clan_service()
    lista_clanes = clan_service.obtener_clanes()
    return render_template('jugador/clanes.html', clanes=lista_clanes)

@clanes_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    logo_url = request.form.get('logo_url')
    banner_url = request.form.get('banner_url')
    privacidad = request.form.get('privacidad', 'publico')
    
    sf = get_service_factory()
    clan_service = sf.get_clan_service()
    
    try:
        nuevo_clan = clan_service.crear_clan(
            lider_id=current_user.id_usuario,
            nombre=nombre,
            descripcion=descripcion,
            logo_url=logo_url,
            banner_url=banner_url,
            privacidad=privacidad
        )
        flash(f'¡El clan "{nuevo_clan.nombre}" se creó con éxito! Ahora eres el Líder.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
        
    return redirect(url_for('clanes.index'))

@clanes_bp.route('/unirse/<int:clan_id>', methods=['POST'])
@login_required
def unirse(clan_id):
    sf = get_service_factory()
    clan_service = sf.get_clan_service()
    
    try:
        clan, accion = clan_service.unirse_clan(clan_id, current_user.id_usuario)
        if accion == 'solicitud':
            flash(f'Tu solicitud ha sido enviada al clan {clan.nombre}. Espera a que el líder te acepte.', 'success')
        else:
            flash(f'¡Felicidades! Te has unido exitosamente al clan {clan.nombre}.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
        
    return redirect(url_for('clanes.detalle', clan_id=clan_id))

@clanes_bp.route('/<int:clan_id>')
def detalle(clan_id):
    from app.models.clan import Clan
    clan = Clan.query.get_or_404(clan_id)
    return render_template('jugador/clan_detalle.html', clan=clan)
    
@clanes_bp.route('/solicitud/<int:solicitud_id>/<string:accion>', methods=['POST'])
@login_required
def gestionar_solicitud(solicitud_id, accion):
    sf = get_service_factory()
    clan_service = sf.get_clan_service()
    
    try:
        solicitud = clan_service.gestionar_solicitud(solicitud_id, current_user.id_usuario, accion)
        if accion == 'aceptar':
            flash(f'Has aceptado a {solicitud.usuario.username} en tu clan.', 'success')
        else:
            flash(f'Has rechazado la solicitud de {solicitud.usuario.username}.', 'info')
    except ValueError as e:
        flash(str(e), 'error')
        
    from urllib.parse import urlparse
    ref = request.referrer
    if ref:
        parsed = urlparse(ref)
        if parsed.netloc and parsed.netloc != request.host:
            ref = None
    return redirect(ref or url_for('clanes.index'))

@clanes_bp.route('/abandonar/<int:clan_id>', methods=['POST'])
@login_required
def abandonar(clan_id):
    sf = get_service_factory()
    clan_service = sf.get_clan_service()
    
    try:
        clan_service.abandonar_clan(clan_id, current_user.id_usuario)
        flash('Has abandonado el clan exitosamente.', 'info')
    except ValueError as e:
        flash(str(e), 'error')
        
    return redirect(url_for('clanes.index'))

@clanes_bp.route('/<int:clan_id>/editar', methods=['POST'])
@login_required
def editar(clan_id):
    sf = get_service_factory()
    clan_service = sf.get_clan_service()
    
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    logo_url = request.form.get('logo_url')
    banner_url = request.form.get('banner_url')
    privacidad = request.form.get('privacidad')
    
    try:
        clan_service.editar_clan(clan_id, current_user.id_usuario, nombre, descripcion, logo_url, banner_url, privacidad)
        flash("Configuración del clan guardada correctamente.", "success")
    except ValueError as e:
        flash(str(e), "error")
        
    return redirect(url_for('clanes.detalle', clan_id=clan_id))

@clanes_bp.route('/<int:clan_id>/expulsar/<int:usuario_id>', methods=['POST'])
@login_required
def expulsar(clan_id, usuario_id):
    sf = get_service_factory()
    clan_service = sf.get_clan_service()
    try:
        clan_service.expulsar_miembro(clan_id, current_user.id_usuario, usuario_id)
        flash("El miembro ha sido expulsado del clan.", "info")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for('clanes.detalle', clan_id=clan_id))

@clanes_bp.route('/<int:clan_id>/transferir_mando/<int:usuario_id>', methods=['POST'])
@login_required
def transferir_mando(clan_id, usuario_id):
    sf = get_service_factory()
    clan_service = sf.get_clan_service()
    try:
        clan_service.transferir_liderazgo(clan_id, current_user.id_usuario, usuario_id)
        flash("La corona ha sido entregada. Ahora eres un administrador.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for('clanes.detalle', clan_id=clan_id))

from flask import jsonify

@clanes_bp.route('/<int:clan_id>/chat', methods=['POST'])
@login_required
def enviar_mensaje_clan(clan_id):
    from app.models.clan import MiembroClan, MensajeClan
    from app.factories.app_factory import db
    
    es_miembro = MiembroClan.query.filter_by(clan_id=clan_id, usuario_id=current_user.id_usuario).first()
    if not es_miembro:
        return jsonify({"error": "No eres miembro de este clan"}), 403
        
    data = request.get_json()
    contenido = data.get('contenido', '').strip()
    if contenido:
        nuevo_msg = MensajeClan(clan_id=clan_id, usuario_id=current_user.id_usuario, contenido=contenido)
        db.session.add(nuevo_msg)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Mensaje vacío"}), 400

@clanes_bp.route('/<int:clan_id>/post', methods=['POST'])
@login_required
def publicar_muro_clan(clan_id):
    from app.models.clan import MiembroClan, PublicacionClan, Clan
    from app.factories.app_factory import db
    
    es_miembro = MiembroClan.query.filter_by(clan_id=clan_id, usuario_id=current_user.id_usuario).first()
    if not es_miembro:
        return jsonify({"error": "No eres miembro de este clan"}), 403
        
    data = request.get_json()
    contenido = data.get('contenido', '').strip()
    if contenido:
        nueva_pub = PublicacionClan(clan_id=clan_id, usuario_id=current_user.id_usuario, contenido=contenido)
        db.session.add(nueva_pub)
        
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Contenido vacío"}), 400
