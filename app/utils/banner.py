"""Banner de perfil por defecto (RiftZone original)."""

import os
import uuid
from werkzeug.utils import secure_filename

DEFAULT_PROFILE_BANNER = '/static/img/default_banner.png'


def profile_banner_url(banner):
    """Devuelve el banner del usuario o el predeterminado si no tiene uno."""
    if not banner or not str(banner).strip():
        return DEFAULT_PROFILE_BANNER
    return str(banner).strip()


def save_banner_photo(file, user_id, upload_folder):
    """
    Guarda el banner de perfil en static/uploads.
    Retorna la ruta relativa (/static/uploads/...) o None si falla.
    Solo permite imágenes estáticas (PNG, JPG, JPEG).
    """
    if not file or not file.filename:
        return None

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext not in {'png', 'jpg', 'jpeg'}:
        return None

    os.makedirs(upload_folder, exist_ok=True)
    unique_filename = f'banner_{user_id}_{uuid.uuid4().hex[:8]}.{ext}'
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return f'/static/uploads/{unique_filename}'
