import os
import uuid
import struct
from datetime import timedelta
from flask import current_app, url_for

try:
    from PIL import Image, UnidentifiedImageError
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXT = {'mp4', 'mov', 'avi', 'webm'}
MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 200 * 1024 * 1024
MAX_VIDEO_DURATION_SEC = 120
IMAGE_MAX_WIDTH = 1200
IMAGE_QUALITY = 80
UPLOAD_SUBDIRS = {'image': 'images', 'video': 'videos'}


def _ext(filename):
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def _random_filename(ext, prefix='media'):
    return f'{prefix}_{uuid.uuid4().hex[:16]}.{ext}'


def _ensure_dir(subdir):
    d = os.path.join(current_app.static_folder, 'uploads', subdir)
    os.makedirs(d, exist_ok=True)
    return d


def _parse_video_duration(filepath):
    """Read video duration from MP4/MOV moov atom or AVI header."""
    ext = _ext(filepath)
    try:
        if ext in ('mp4', 'mov'):
            return _moov_duration(filepath)
        elif ext == 'avi':
            return _avi_duration(filepath)
    except Exception:
        pass
    return None


def _moov_duration(filepath):
    """Parse MP4/MOV moov atom for duration."""
    with open(filepath, 'rb') as f:
        data = f.read(1048576)
    i = 0
    while i < len(data) - 8:
        box_size = struct.unpack('>I', data[i:i+4])[0]
        box_type = data[i+4:i+8]
        if box_type == b'moov':
            sub = i
            while sub < min(i + (box_size or len(data)), len(data)) - 8:
                ss = struct.unpack('>I', data[sub:sub+4])[0]
                st = data[sub+4:sub+8]
                if st == b'mvhd':
                    version = data[sub+8]
                    if version == 0:
                        timescale = struct.unpack('>I', data[sub+20:sub+24])[0]
                        duration = struct.unpack('>I', data[sub+24:sub+28])[0]
                    else:
                        timescale = struct.unpack('>I', data[sub+28:sub+32])[0]
                        duration = struct.unpack('>Q', data[sub+32:sub+40])[0]
                    if timescale > 0:
                        return duration / timescale
                    return None
                sub += ss or 1
        i += box_size or 1
    return None


def _avi_duration(filepath):
    """Parse AVI header for duration."""
    with open(filepath, 'rb') as f:
        header = f.read(2048)
    idx = header.find(b'movi')
    if idx == -1:
        idx = header.find(b'LIST')
    if idx == -1:
        return None
    try:
        rate_pos = header.find(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80@')
        if rate_pos == -1:
            micro_sec = struct.unpack('<I', header[40:44])[0]
        else:
            micro_sec = struct.unpack('<d', header[rate_pos+12:rate_pos+20])[0]
        total_frames = struct.unpack('<I', header[48:52])[0]
        if micro_sec > 0:
            return (total_frames * micro_sec) / 1000000
    except Exception:
        pass
    return None


def _compress_image(filepath):
    """Compress image in-place. Requires Pillow."""
    if not HAS_PILLOW:
        return
    try:
        img = Image.open(filepath)
        img = img.convert('RGB') if img.mode in ('RGBA', 'P') else img
        if img.width > IMAGE_MAX_WIDTH:
            ratio = IMAGE_MAX_WIDTH / img.width
            img = img.resize((IMAGE_MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
        ext = _ext(filepath)
        if ext == 'png':
            img.save(filepath, 'PNG', optimize=True)
        elif ext in ('jpg', 'jpeg'):
            img.save(filepath, 'JPEG', quality=IMAGE_QUALITY, optimize=True)
        elif ext == 'webp':
            img.save(filepath, 'WEBP', quality=IMAGE_QUALITY)
        elif ext == 'gif':
            img.save(filepath, 'GIF', optimize=True)
    except (UnidentifiedImageError, Exception):
        pass


def upload_media(file_obj, media_type='image'):
    """
    Upload and process a media file.
    Returns dict with 'url' on success, or 'error' on failure.
    """
    if not file_obj or not file_obj.filename:
        return {'error': 'No se envió ningún archivo.'}

    ext = _ext(file_obj.filename)
    if media_type == 'image':
        if ext not in ALLOWED_IMAGE_EXT:
            return {'error': f'Formato de imagen no válido ({ext}). Permitidos: {", ".join(sorted(ALLOWED_IMAGE_EXT))}.'}
        if not file_obj.content_type or not file_obj.content_type.startswith('image/'):
            return {'error': 'El archivo no es una imagen válida.'}
    elif media_type == 'video':
        if ext not in ALLOWED_VIDEO_EXT:
            return {'error': f'Formato de video no válido ({ext}). Permitidos: {", ".join(sorted(ALLOWED_VIDEO_EXT))}.'}
        if not file_obj.content_type or not file_obj.content_type.startswith('video/'):
            return {'error': 'El archivo no es un video válido.'}
    else:
        return {'error': 'Tipo de medio no soportado.'}

    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)

    if media_type == 'image' and size > MAX_IMAGE_SIZE:
        return {'error': f'La imagen excede el límite de {MAX_IMAGE_SIZE // (1024*1024)} MB.'}
    if media_type == 'video' and size > MAX_VIDEO_SIZE:
        return {'error': f'El video excede el límite de {MAX_VIDEO_SIZE // (1024*1024)} MB.'}

    subdir = UPLOAD_SUBDIRS.get(media_type, 'images')
    upload_dir = _ensure_dir(subdir)
    filename = _random_filename(ext, f'post_{media_type}')
    filepath = os.path.join(upload_dir, filename)
    file_obj.save(filepath)

    if media_type == 'image':
        _compress_image(filepath)
    elif media_type == 'video':
        duration = _parse_video_duration(filepath)
        if duration and duration > MAX_VIDEO_DURATION_SEC:
            os.remove(filepath)
            return {'error': f'El video excede la duración máxima de {MAX_VIDEO_DURATION_SEC} segundos ({timedelta(seconds=int(duration))}).'}

    file_url = url_for('static', filename=f'uploads/{subdir}/{filename}')
    return {'url': file_url, 'filename': filename}