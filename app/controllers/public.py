from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__, template_folder='../templates/public')

@public_bp.route('/')
def home():
    return render_template('jugador/dashboard.html')

@public_bp.route('/buscar')
def buscar():
    from flask import request, redirect, url_for, flash
    from app.factories.service_factory import get_service_factory
    
    query = request.args.get('q')
    if not query:
        return redirect(request.referrer or url_for('public.home'))
        
    sf = get_service_factory()
    user_service = sf.get_usuario_service()
    resultados = user_service.search_users(query)
    
    if not resultados:
        flash(f'No se encontró ningún jugador con el nombre "{query}".', 'error')
        return redirect(request.referrer or url_for('public.home'))
        
    # Redirigir al primer resultado encontrado (para búsqueda rápida)
    primer_resultado = resultados[0]
    return redirect(url_for('jugador.perfil_publico', username=primer_resultado.username))
