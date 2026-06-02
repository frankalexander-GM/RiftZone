from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user

public_bp = Blueprint('public', __name__, template_folder='../templates/public')

@public_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('jugador.dashboard'))
    return redirect(url_for('auth.login'))

@public_bp.route('/buscar')
def buscar():
    from flask import request, render_template
    from app.factories.service_factory import get_service_factory
    from app.models.clan import Clan
    
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('public/buscar.html', query='', usuarios=[], clanes=[], juegos=[])
    
    sf = get_service_factory()
    user_service = sf.get_usuario_service()
    usuarios = user_service.search_users(query)
    
    clanes = Clan.query.filter(Clan.nombre.ilike(f'%{query}%')).all()
    
    # Buscar en juegos/comunidades (case-insensitive)
    from app.factories.app_factory import db
    ql = query.lower()
    juegos_encontrados = []
    todos_los_juegos = [
        "Counter-Strike 2", "Valorant", "Rainbow Six Siege", "Overwatch 2",
        "The Finals", "Destiny 2", "Call of Duty: Black Ops 6", "Team Fortress 2",
        "Battlefield 2042", "Escape from Tarkov", "Hunt: Showdown", "Splitgate",
        "XDefiant", "Fortnite", "Call of Duty: Warzone", "Apex Legends",
        "PUBG: Battlegrounds", "Free Fire", "Fall Guys", "Call of Duty Mobile",
        "Stumble Guys", "League of Legends", "Dota 2", "Mobile Legends: Bang Bang",
        "Honor of Kings", "Genshin Impact", "Warframe", "World of Warcraft",
        "Final Fantasy XIV", "Baldur's Gate 3", "Diablo IV", "Path of Exile",
        "Lost Ark", "Black Desert Online", "Elden Ring", "Minecraft", "Roblox",
        "GTA V / GTA Online", "Palworld", "ARK: Survival Evolved", "Rust",
        "Terraria", "Valheim", "No Man's Sky", "Red Dead Redemption 2",
        "Cyberpunk 2077", "Sea of Thieves", "The Forest",
        "EA Sports FC 26", "Rocket League", "Helldivers 2", "Among Us",
        "Dead by Daylight", "Phasmophobia", "Lethal Company", "Brawlhalla",
        "Street Fighter 6", "Tekken 8", "Mario Kart 8 Deluxe",
        "Gran Turismo 7", "Forza Horizon 5",
    ]
    for juego in todos_los_juegos:
        if ql in juego.lower():
            juegos_encontrados.append({
                "nombre": juego,
                "carpeta": "shooters",
                "categoria": "Juegos"
            })
    
    return render_template('public/buscar.html', query=query, usuarios=usuarios, clanes=clanes, juegos=juegos_encontrados)
