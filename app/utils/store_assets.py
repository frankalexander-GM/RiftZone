"""Subida de diseños de la tienda y estilos aplicables al perfil."""
import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_STORE_EXT = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

COLORES_PRESET = {
    'rosa': '#FF2D95',
    'rojo': '#EF4444',
    'morado': '#8B5CF6',
    'azul': '#3B82F6',
    'cyan': '#00E5FF',
    'verde': '#10B981',
    'dorado': '#FACC15',
    'naranja': '#FF6600',
}


def normalize_hex(color):
    if not color:
        return COLORES_PRESET['rosa']
    c = str(color).strip()
    if c in COLORES_PRESET:
        return COLORES_PRESET[c]
    if not c.startswith('#'):
        c = f'#{c}'
    if len(c) in (4, 7):
        return c
    return COLORES_PRESET['rosa']


def build_css_class(category, color_hex, glow=10, border_width=3):
    """Genera estilos inline que se guardan en store_items.css_class."""
    color = normalize_hex(color_hex)
    if category == 'frame':
        return (
            f'border: {border_width}px solid {color}; '
            f'box-shadow: 0 0 {glow}px {color};'
        )
    if category == 'title':
        return (
            f'color: {color}; font-weight: 900; '
            f'text-shadow: 0 0 8px {color};'
        )
    return ''


def save_store_image(file, upload_folder, prefix='item'):
    """Guarda imagen de marco/fondo. Retorna ruta /static/uploads/store/..."""
    if not file or not file.filename:
        return None

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_STORE_EXT:
        return None

    store_dir = os.path.join(upload_folder, 'store')
    os.makedirs(store_dir, exist_ok=True)
    unique = f'{prefix}_{uuid.uuid4().hex[:10]}.{ext}'
    filepath = os.path.join(store_dir, unique)
    file.save(filepath)
    return f'/static/uploads/store/{unique}'
