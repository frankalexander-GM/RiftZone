from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.factories.app_factory import db
from app.models.mensaje_privado import MensajePrivado
from app.models.usuario import Usuario
from datetime import datetime

mensajes_bp = Blueprint('mensajes', __name__, template_folder='../templates/jugador')


@mensajes_bp.route('/mensajes')
@login_required
def index():
    return render_template('mensajes.html')


@mensajes_bp.route('/mensajes/api/conversaciones')
@login_required
def conversaciones():
    user_id = current_user.id_usuario
    # Obtener IDs de los usuarios con los que hemos conversado
    subquery = db.session.query(
        db.case(
            (MensajePrivado.emisor_id == user_id, MensajePrivado.receptor_id),
            else_=MensajePrivado.emisor_id
        ).label('otro_id'),
        db.func.max(MensajePrivado.creado_en).label('ultimo')
    ).filter(
        (MensajePrivado.emisor_id == user_id) | (MensajePrivado.receptor_id == user_id)
    ).group_by('otro_id').subquery()

    from sqlalchemy import func
    conversaciones = db.session.query(
        Usuario,
        MensajePrivado.contenido,
        subquery.c.ultimo,
        db.func.count(
            db.case(
                (MensajePrivado.leido == False, MensajePrivado.id_mensaje),
                else_=None
            )
        ).label('no_leidas')
    ).join(subquery, Usuario.id_usuario == subquery.c.otro_id
    ).join(MensajePrivado, (MensajePrivado.creado_en == subquery.c.ultimo) & (
        ((MensajePrivado.emisor_id == user_id) & (MensajePrivado.receptor_id == Usuario.id_usuario)) |
        ((MensajePrivado.receptor_id == user_id) & (MensajePrivado.emisor_id == Usuario.id_usuario))
    )).filter(
        (MensajePrivado.emisor_id == user_id) | (MensajePrivado.receptor_id == user_id)
    ).group_by(Usuario.id_usuario, Usuario.username, Usuario.nombre, Usuario.foto_perfil,
               Usuario.es_premium, MensajePrivado.contenido, subquery.c.ultimo
    ).order_by(subquery.c.ultimo.desc()).all()

    resultado = []
    for u, ultimo_msg, ultimo_time, no_leidas in conversaciones:
        from app.utils.avatar import avatar_url
        from app.services.boost_service import color_nombre_boost
        resultado.append({
            'usuario_id': u.id_usuario,
            'username': u.username,
            'nombre': u.nombre or u.username,
            'foto': avatar_url(u.foto_perfil),
            'ultimo_mensaje': ultimo_msg[:80] + '...' if ultimo_msg and len(ultimo_msg) > 80 else (ultimo_msg or ''),
            'ultimo_time': ultimo_time.strftime('%H:%M') if ultimo_time else '',
            'ultimo_time_completo': ultimo_time.strftime('%d/%m/%Y %H:%M') if ultimo_time else '',
            'no_leidas': no_leidas or 0,
            'es_premium': bool(u.es_premium),
            'boost_color': color_nombre_boost(u.id_usuario),
        })
    return jsonify(resultado)


@mensajes_bp.route('/mensajes/api/mensajes/<int:otro_id>')
@login_required
def obtener_mensajes(otro_id):
    user_id = current_user.id_usuario
    mensajes = MensajePrivado.query.filter(
        ((MensajePrivado.emisor_id == user_id) & (MensajePrivado.receptor_id == otro_id)) |
        ((MensajePrivado.receptor_id == user_id) & (MensajePrivado.emisor_id == otro_id))
    ).order_by(MensajePrivado.creado_en.asc()).limit(100).all()

    # Marcar como leídos los mensajes recibidos de ese usuario
    MensajePrivado.query.filter(
        (MensajePrivado.emisor_id == otro_id) &
        (MensajePrivado.receptor_id == user_id) &
        (MensajePrivado.leido == False)
    ).update({'leido': True})
    db.session.commit()

    return jsonify([m.to_dict() for m in mensajes])


@mensajes_bp.route('/mensajes/api/enviar', methods=['POST'])
@login_required
def enviar():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos inválidos'}), 400
    receptor_id = data.get('receptor_id')
    contenido = data.get('contenido', '').strip()
    if not receptor_id or not contenido:
        return jsonify({'error': 'Faltan datos'}), 400
    if len(contenido) > 1000:
        return jsonify({'error': 'Mensaje muy largo (máx 1000 caracteres)'}), 400
    receptor = Usuario.query.get(receptor_id)
    if not receptor:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    msg = MensajePrivado(
        emisor_id=current_user.id_usuario,
        receptor_id=receptor_id,
        contenido=contenido
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify(msg.to_dict())


@mensajes_bp.route('/mensajes/api/buscar')
@login_required
def buscar_usuarios():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    usuarios = Usuario.query.filter(
        (Usuario.username.ilike(f'%{q}%')) | (Usuario.nombre.ilike(f'%{q}%'))
    ).limit(10).all()

    from app.utils.avatar import avatar_url
    from app.services.boost_service import color_nombre_boost
    resultado = []
    for u in usuarios:
        if u.id_usuario == current_user.id_usuario:
            continue
        resultado.append({
            'usuario_id': u.id_usuario,
            'username': u.username,
            'nombre': u.nombre or u.username,
            'foto': avatar_url(u.foto_perfil),
            'es_premium': bool(u.es_premium),
            'boost_color': color_nombre_boost(u.id_usuario),
        })
    return jsonify(resultado)