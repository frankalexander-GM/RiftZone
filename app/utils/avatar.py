import os

DEFAULT_AVATAR = (
    'https://images.unsplash.com/photo-1566577739112-5180d4bf9390'
    '?q=80&w=200&auto=format&fit=crop'
)


def avatar_url(foto_perfil):
    """URL de avatar con bust de caché para archivos locales."""
    if not foto_perfil or not str(foto_perfil).strip():
        return DEFAULT_AVATAR
    url = str(foto_perfil).strip()
    if url.startswith('/static/'):
        base, _, query = url.partition('?')
        token = abs(hash(base))
        if query:
            return f'{url}&v={token}'
        return f'{url}?v={token}'
    return url


def save_profile_photo(file, user_id, upload_folder):
    """
    Guarda la foto de perfil en static/uploads.
    Retorna la ruta relativa (/static/uploads/...) o None si falla.
    """
    import uuid
    from werkzeug.utils import secure_filename

    if not file or not file.filename:
        return None

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext not in {'png', 'jpg', 'jpeg'}:
        return None

    os.makedirs(upload_folder, exist_ok=True)
    unique_filename = f'avatar_{user_id}_{uuid.uuid4().hex[:8]}.{ext}'
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return f'/static/uploads/{unique_filename}'
