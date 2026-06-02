"""Sincronización de cosméticos (marco, banner, título de tienda)."""

import re

ROLES_PERFIL = frozenset({
    'Gamer', 'Streamer', 'Pro Player', 'Creador', 'Caster', 'Diseñador',
})

# Color del nombre = mismo tono que la etiqueta del perfil
COLOR_NOMBRE_POR_ROL = {
    'Gamer': '#10B981',
    'Streamer': '#EF4444',
    'Pro Player': '#FBBF24',
    'Creador': '#3B82F6',
    'Caster': '#8B5CF6',
    'Diseñador': '#EC4899',
}


def titulo_desde_item(nombre_item):
    """'Título: Dios del Aim' → 'Dios del Aim'."""
    if not nombre_item:
        return 'Gamer'
    return nombre_item.replace('Título: ', '').strip() or 'Gamer'


def es_titulo_de_tienda(titulo):
    if not titulo:
        return False
    t = titulo.strip()
    if t.upper().startswith('VIP'):
        return False
    return t not in ROLES_PERFIL


def sync_inventory_equipped(user):
    """Alinea is_equipped con lo que el usuario tiene puesto en el perfil."""
    from app.factories.app_factory import db
    from app.models.tienda import UserInventory

    inventario = UserInventory.query.filter_by(user_id=user.id_usuario).all()
    titulo_actual = (user.titulo_perfil or 'Gamer').strip()
    banner_actual = (user.banner or '').strip()
    marco_actual = (user.marco_perfil or '').strip()

    for inv in inventario:
        cat = inv.item.category
        if cat == 'title':
            inv.is_equipped = titulo_actual == titulo_desde_item(inv.item.name)
        elif cat == 'background':
            img = (inv.item.image_url or '').strip()
            inv.is_equipped = bool(img) and banner_actual == img
        elif cat == 'frame':
            css = (inv.item.css_class or '').strip()
            inv.is_equipped = bool(css) and marco_actual == css

    db.session.commit()


def get_equipped_title_cosmetic(user):
    """Devuelve dict con label y css_class del título de tienda equipado, si aplica."""
    from app.models.tienda import UserInventory, StoreItem

    if not es_titulo_de_tienda(user.titulo_perfil):
        return None

    inv = (
        UserInventory.query.filter_by(user_id=user.id_usuario, is_equipped=True)
        .join(StoreItem)
        .filter(StoreItem.category == 'title')
        .first()
    )
    if inv:
        return {
            'label': titulo_desde_item(inv.item.name),
            'css_class': inv.item.css_class or '',
        }

    titulo = (user.titulo_perfil or 'Gamer').strip()
    item = _buscar_item_titulo_tienda(titulo)
    if item and item.css_class:
        return {
            'label': titulo,
            'css_class': item.css_class or '',
        }

    return {
        'label': titulo,
        'css_class': '',
    }


def _buscar_item_titulo_tienda(titulo):
    from app.models.tienda import StoreItem

    if not titulo or not es_titulo_de_tienda(titulo):
        return None
    nombre_item = f'Título: {titulo}'
    return StoreItem.query.filter_by(category='title', name=nombre_item).first()


def _color_desde_css(css):
    if not css:
        return None
    match = re.search(r'color:\s*([^;]+)', css, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip()


def _color_seguro(color):
    if not color:
        return False
    c = color.strip()
    if re.match(r'^#[0-9A-Fa-f]{3,8}$', c):
        return True
    return c.lower() in {
        'white', '#fff', '#ffffff',
        'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 'pink',
    }


def color_nombre_etiqueta(user):
    """Color hex del nombre según título/etiqueta equipada (tienda o rol del perfil)."""
    if user is None:
        return None

    titulo_cos = get_equipped_title_cosmetic(user)
    if titulo_cos and titulo_cos.get('css_class'):
        color = _color_desde_css(titulo_cos['css_class'])
        if _color_seguro(color):
            return color

    titulo = (user.titulo_perfil or 'Gamer').strip()
    if titulo.upper().startswith('VIP'):
        return None

    if titulo in COLOR_NOMBRE_POR_ROL:
        return COLOR_NOMBRE_POR_ROL[titulo]

    if es_titulo_de_tienda(titulo):
        item = _buscar_item_titulo_tienda(titulo)
        if item and item.color_hex:
            from app.utils.store_assets import normalize_hex
            return normalize_hex(item.color_hex)

    return None


def estilo_nombre_usuario(user):
    """Estilos inline seguros solo para el texto del nombre (no usar en chat)."""
    from app.services.boost_service import color_nombre_boost
    boost_color = color_nombre_boost(user.id_usuario) if user else None
    if boost_color:
        return f'color: {boost_color}; font-weight: 800; text-shadow: 0 0 8px {boost_color};'
    color = color_nombre_etiqueta(user)
    if not color:
        return ''
    return f'color: {color}; font-weight: 800; text-shadow: 0 0 8px {color};'


def texto_nombre_usuario(user):
    if user is None:
        return 'Usuario'
    return (user.nombre or user.username or 'Usuario').strip()
