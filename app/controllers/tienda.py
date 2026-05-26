from functools import wraps

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, login_user
from app.factories.app_factory import db
from app.models.tienda import StoreItem, UserInventory
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario

tienda_bp = Blueprint('tienda', __name__)

from app.utils.banner import DEFAULT_PROFILE_BANNER
from app.utils.cosmetics import sync_inventory_equipped, titulo_desde_item


def _vip_marco_for_user(user):
    """Restaura el marco VIP de membresía, si aplica."""
    membresia = getattr(user, 'membresia_tipo', None) or 'ninguna'
    if membresia == 'plata':
        return 'border: 2px solid #C0C0C0; box-shadow: 0 0 8px #C0C0C0;'
    if membresia == 'oro':
        return 'border: 2px solid #FACC15; box-shadow: 0 0 10px #FACC15;'
    if membresia == 'diamante':
        return 'border: 3px solid #00E5FF; box-shadow: 0 0 15px #00E5FF;'
    return None


def _clear_cosmetic(user, category, restore_vip_frame=False):
    if category == 'background':
        user.banner = DEFAULT_PROFILE_BANNER
    elif category == 'title':
        user.titulo_perfil = 'Gamer'
    elif category == 'frame':
        user.marco_perfil = _vip_marco_for_user(user) if restore_vip_frame else None


def _apply_cosmetic(user, inv_item):
    category = inv_item.item.category
    if category == 'background':
        user.banner = inv_item.item.image_url
    elif category == 'title':
        user.titulo_perfil = titulo_desde_item(inv_item.item.name)
    elif category == 'frame':
        user.marco_perfil = inv_item.item.css_class


def _refresh_session_user(user):
    db.session.refresh(user)
    login_user(user, remember=True)


def _puede_gestionar_tienda():
    """Solo administradores pueden subir diseños a la tienda."""
    if not current_user.is_authenticated:
        return False
    return current_user.is_admin()


def gestor_tienda_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not _puede_gestionar_tienda():
            flash('Solo los administradores pueden subir diseños a la tienda.', 'error')
            return redirect(url_for('tienda.index'))
        return f(*args, **kwargs)
    return wrapped


@tienda_bp.route('/')
@login_required
def index():
    # Obtener filtros y ordenamiento de la query
    cat_filter = request.args.get('cat', 'all')
    order = request.args.get('order', 'price-asc')

    # Base query de items
    query = StoreItem.query
    if cat_filter != 'all':
        query = query.filter_by(category=cat_filter)
    # Ordenar
    if order == 'price-asc':
        query = query.order_by(StoreItem.price.asc())
    elif order == 'price-desc':
        query = query.order_by(StoreItem.price.desc())
    items = query.all()

    # Obtener inventario del usuario
    inventario = UserInventory.query.filter_by(user_id=current_user.id_usuario).all()
    comprados_ids = [inv.item_id for inv in inventario]

    # Calcular descuento por membresía
    descuento = 0
    membresia = current_user.membresia_tipo
    if membresia == 'plata':
        descuento = 0.10
    elif membresia in ['oro', 'diamante']:
        descuento = 0.20

    return render_template(
        'tienda/index.html',
        items=items,
        comprados_ids=comprados_ids,
        descuento=descuento,
        cat_filter=cat_filter,
        order=order,
        puede_gestionar=_puede_gestionar_tienda(),
    )

@tienda_bp.route('/comprar/<int:item_id>', methods=['POST'])
@login_required
def comprar(item_id):
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'message': 'Los invitados no pueden comprar artículos.'}), 403
        
    item = StoreItem.query.get_or_404(item_id)
    
    # Verificar si ya lo tiene
    if UserInventory.query.filter_by(user_id=current_user.id_usuario, item_id=item_id).first():
        return jsonify({'success': False, 'message': 'Ya posees este artículo.'}), 400
        
    # Verificar stock disponible
    if item.stock is not None and item.stock <= 0:
        return jsonify({'success': False, 'message': 'Este artículo está agotado.'}), 400
    # Calcular precio final
    descuento = 0
    membresia = current_user.membresia_tipo
    if membresia == 'plata':
        descuento = 0.10
    elif membresia in ['oro', 'diamante']:
        descuento = 0.20
    precio_final = int(item.price * (1 - descuento))
    if current_user.tokens < precio_final:
        return jsonify({'success': False, 'message': 'No tienes suficientes RiftCoins.'}), 400
    try:
        # Restar tokens
        current_user.tokens -= precio_final
        # Decrementar stock
        if item.stock is not None:
            item.stock -= 1
        # Registrar compra
        tx = Transaccion(
            user_id=current_user.id_usuario,
            amount=-precio_final,
            type='egreso',
            description=f'Compra en tienda: {item.name}'
        )
        db.session.add(tx)
        # Añadir al inventario
        nuevo_item = UserInventory(
            user_id=current_user.id_usuario,
            item_id=item_id
        )
        db.session.add(nuevo_item)
        db.session.commit()
        return jsonify({'success': True, 'message': '¡Artículo adquirido con éxito!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al procesar la compra.'}), 500

@tienda_bp.route('/inventario')
@login_required
def inventario():
    sync_inventory_equipped(current_user)
    inventario_items = UserInventory.query.filter_by(user_id=current_user.id_usuario).all()
    return render_template('tienda/inventario.html', inventario=inventario_items)

@tienda_bp.route('/equipar/<int:inventory_id>', methods=['POST'])
@login_required
def equipar(inventory_id):
    inv_item = UserInventory.query.get_or_404(inventory_id)

    if inv_item.user_id != current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403

    item_category = inv_item.item.category

    try:
        anteriores = UserInventory.query.filter_by(
            user_id=current_user.id_usuario, is_equipped=True
        ).all()
        for ant in anteriores:
            if ant.item.category == item_category:
                ant.is_equipped = False

        inv_item.is_equipped = True
        _apply_cosmetic(current_user, inv_item)

        db.session.commit()
        sync_inventory_equipped(current_user)
        _refresh_session_user(current_user)
        return jsonify({'success': True, 'message': f'¡{inv_item.item.name} equipado en tu perfil!'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al equipar el artículo.'}), 500


@tienda_bp.route('/desequipar/<int:inventory_id>', methods=['POST'])
@login_required
def desequipar(inventory_id):
    inv_item = UserInventory.query.get_or_404(inventory_id)

    if inv_item.user_id != current_user.id_usuario:
        return jsonify({'success': False, 'message': 'No tienes permiso.'}), 403

    if not inv_item.is_equipped:
        return jsonify({'success': False, 'message': 'Este artículo no está equipado.'}), 400

    item_category = inv_item.item.category

    try:
        inv_item.is_equipped = False
        _clear_cosmetic(current_user, item_category, restore_vip_frame=True)

        db.session.commit()
        sync_inventory_equipped(current_user)
        _refresh_session_user(current_user)
        return jsonify({
            'success': True,
            'message': f'¡{inv_item.item.name} desequipado! Tu perfil volvió al título Gamer.',
        })
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al desequipar el artículo.'}), 500


@tienda_bp.route('/admin')
@login_required
@gestor_tienda_required
def admin_tienda():
    from app.utils.store_assets import COLORES_PRESET
    items = StoreItem.query.order_by(StoreItem.id.desc()).all()
    return render_template(
        'tienda/admin.html',
        items=items,
        colores=COLORES_PRESET,
    )


@tienda_bp.route('/admin/crear', methods=['POST'])
@login_required
@gestor_tienda_required
def admin_crear_item():
    from app.utils.store_assets import build_css_class, save_store_image, normalize_hex

    nombre = (request.form.get('name') or '').strip()
    categoria = (request.form.get('category') or 'frame').strip().lower()
    precio = request.form.get('price', type=int) or 0
    stock = request.form.get('stock', type=int)
    if stock is None:
        stock = 10
    color = request.form.get('color_hex') or request.form.get('color') or 'rosa'

    if not nombre:
        flash('El nombre del diseño es obligatorio.', 'error')
        return redirect(url_for('tienda.admin_tienda'))
    if categoria not in ('frame', 'background', 'title'):
        flash('Categoría no válida.', 'error')
        return redirect(url_for('tienda.admin_tienda'))
    if precio < 0:
        flash('El precio debe ser 0 o más.', 'error')
        return redirect(url_for('tienda.admin_tienda'))

    if categoria == 'title' and not nombre.lower().startswith('título'):
        nombre = f'Título: {nombre}'

    hex_color = normalize_hex(color)
    css = build_css_class(categoria, hex_color)
    imagen_url = None

    archivo = request.files.get('imagen')
    if categoria in ('frame', 'background'):
        imagen_url = save_store_image(archivo, current_app.config['UPLOAD_FOLDER'])
        if not imagen_url:
            flash('Sube una imagen PNG/JPG para marcos y fondos.', 'error')
            return redirect(url_for('tienda.admin_tienda'))
    elif categoria == 'title' and archivo and archivo.filename:
        imagen_url = save_store_image(archivo, current_app.config['UPLOAD_FOLDER'])

    try:
        item = StoreItem(
            name=nombre,
            category=categoria,
            price=precio,
            stock=stock,
            image_url=imagen_url,
            css_class=css,
            color_hex=hex_color,
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Diseño «{nombre}» publicado en la tienda. Los jugadores ya pueden comprarlo y equiparlo.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error al guardar el diseño.', 'error')

    return redirect(url_for('tienda.admin_tienda'))


@tienda_bp.route('/admin/eliminar/<int:item_id>', methods=['POST'])
@login_required
@gestor_tienda_required
def admin_eliminar_item(item_id):
    item = StoreItem.query.get_or_404(item_id)
    try:
        UserInventory.query.filter_by(item_id=item_id).delete()
        db.session.delete(item)
        db.session.commit()
        flash('Diseño eliminado de la tienda.', 'success')
    except Exception:
        db.session.rollback()
        flash('No se pudo eliminar (puede estar en uso).', 'error')
    return redirect(url_for('tienda.admin_tienda'))
