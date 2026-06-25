def get_game_categories():
    """Returns raw game categories with relative image paths."""
    return [
        {
            "slug": "shooters",
            "titulo": "Fuerza Elite",
            "icono": "fa-crosshairs",
            "color": "#ef4444",
            "descripcion": "Shooters tácticos, precisión y reflejos. La cima del combate competitivo.",
            "juegos": [
                {"nombre": "Counter-Strike 2", "imagen": "img/comunidades/shooters/cs2.jpg", "desc": "Rey de Steam, rompe récords de jugadores simultáneos."},
                {"nombre": "Valorant", "imagen": "img/comunidades/shooters/valorant.jpg", "desc": "Shooter competitivo con comunidad enorme."},
                {"nombre": "Rainbow Six Siege", "imagen": "img/comunidades/shooters/rainbow6.jpg", "desc": "Competitivo táctico mantiene su comunidad."},
                {"nombre": "Overwatch 2", "imagen": "img/comunidades/shooters/overwatch2.jpg", "desc": "Héroes, acción rápida y comunidad global."},
                {"nombre": "The Finals", "imagen": "img/comunidades/shooters/thefinals.jpg", "desc": "Free-to-play que sigue creciendo."},
                {"nombre": "Destiny 2", "imagen": "img/comunidades/shooters/destiny2.jpg", "desc": "Expansiones constantes y modelo live service."},
                {"nombre": "Call of Duty: Black Ops 6", "imagen": "img/comunidades/shooters/bo6.jpg", "desc": "El shooter anual más esperado."},
                {"nombre": "Team Fortress 2", "imagen": "img/comunidades/shooters/tf2.jpg", "desc": "Clásico de Valve con legión de seguidores."},
                {"nombre": "Battlefield 2042", "imagen": "img/comunidades/shooters/bf2042.jpg", "desc": "Combate a gran escala con vehículos y destrucción."},
                {"nombre": "Escape from Tarkov", "imagen": "img/comunidades/shooters/tarkov.jpg", "desc": "Shooter hardcore de extracción."},
                {"nombre": "Hunt: Showdown", "imagen": "img/comunidades/shooters/hunt.jpg", "desc": "Caza de monstruos con ambiente western."},
                {"nombre": "Splitgate", "imagen": "img/comunidades/shooters/splitgate.jpg", "desc": "Halo + Portal. Acción con portales."},
                {"nombre": "XDefiant", "imagen": "img/comunidades/shooters/xdefiant.jpg", "desc": "Shooter arcade de Ubisoft con facciones."},
            ]
        },
        {
            "slug": "battle-royale",
            "titulo": "Reyes de la Batalla",
            "icono": "fa-trophy",
            "color": "#f59e0b",
            "descripcion": "Battle royales masivos. Ultimo en pie, gloria eterna.",
            "juegos": [
                {"nombre": "Fortnite", "imagen": "img/comunidades/shooters/fortnite.jpg", "desc": "Eventos constantes, colaboraciones y nuevos modos."},
                {"nombre": "Call of Duty: Warzone", "imagen": "img/comunidades/shooters/warzone.jpg", "desc": "Battle royale masivo de Activision."},
                {"nombre": "Apex Legends", "imagen": "img/comunidades/shooters/apex.jpg", "desc": "Acción rápida y temporadas constantes."},
                {"nombre": "PUBG: Battlegrounds", "imagen": "img/comunidades/shooters/pubg.jpg", "desc": "El pionero del género battle royale."},
                {"nombre": "Free Fire", "imagen": "img/comunidades/shooters/freefire.jpg", "desc": "El rey de los battle royale para móviles."},
                {"nombre": "Fall Guys", "imagen": "img/comunidades/shooters/fallguys.jpg", "desc": "Battle royale de obstáculos y locura."},
                {"nombre": "Call of Duty Mobile", "imagen": "img/comunidades/shooters/codm.jpg", "desc": "La experiencia CoD en tu celular."},
                {"nombre": "Stumble Guys", "imagen": "img/comunidades/shooters/stumble.jpg", "desc": "Party battle royale con millones de descargas."},
            ]
        },
        {
            "slug": "moba-rpg",
            "titulo": "Tripulacion Legendaria",
            "icono": "fa-hat-wizard",
            "color": "#8b5cf6",
            "descripcion": "MOBA, RPG, MMO y accion. Leyendas que forjan su destino.",
            "juegos": [
                {"nombre": "League of Legends", "imagen": "img/comunidades/shooters/lol.jpg", "desc": "El MOBA mas grande del planeta."},
                {"nombre": "Dota 2", "imagen": "img/comunidades/mobas/dota2.jpg", "desc": "Clasico que sigue dominando Steam."},
                {"nombre": "Mobile Legends: Bang Bang", "imagen": "img/comunidades/shooters/mlbb.jpg", "desc": "El MOBA definitivo para dispositivos moviles."},
                {"nombre": "Honor of Kings", "imagen": "img/comunidades/shooters/hok.jpg", "desc": "El MOBA mas jugado del mundo."},
                {"nombre": "Genshin Impact", "imagen": "img/comunidades/shooters/genshin.jpg", "desc": "RPG gacha de mundo abierto."},
                {"nombre": "Warframe", "imagen": "img/comunidades/shooters/warframe.jpg", "desc": "Una de las comunidades mas fieles."},
                {"nombre": "World of Warcraft", "imagen": "img/comunidades/shooters/wow.jpg", "desc": "El MMO por excelencia."},
                {"nombre": "Final Fantasy XIV", "imagen": "img/comunidades/shooters/ffxiv.jpg", "desc": "MMORPG con historia epica."},
                {"nombre": "Baldur's Gate 3", "imagen": "img/comunidades/shooters/bg3.jpg", "desc": "RPG del ano con comunidad gigante."},
                {"nombre": "Diablo IV", "imagen": "img/comunidades/shooters/d4.jpg", "desc": "Action RPG oscuro y adictivo."},
                {"nombre": "Path of Exile", "imagen": "img/comunidades/shooters/poe.jpg", "desc": "El ARPG mas profundo y gratuito."},
                {"nombre": "Lost Ark", "imagen": "img/comunidades/shooters/lostark.jpg", "desc": "MMOARPG con combate espectacular."},
                {"nombre": "Black Desert Online", "imagen": "img/comunidades/shooters/bdo.jpg", "desc": "MMO sandbox con combate fluido."},
                {"nombre": "Elden Ring", "imagen": "img/comunidades/shooters/eldenring.jpg", "desc": "El fenomeno soulslike de mundo abierto."},
            ]
        },
        {
            "slug": "sandbox",
            "titulo": "Constructores de Mundos",
            "icono": "fa-cubes",
            "color": "#10b981",
            "descripcion": "Sandbox, supervivencia y libertad total. Crea tu propia historia.",
            "juegos": [
                {"nombre": "Minecraft", "imagen": "img/comunidades/shooters/minecraft.jpg", "desc": "Fenomeno eterno con millones de jugadores diarios."},
                {"nombre": "Roblox", "imagen": "img/comunidades/shooters/roblox.jpg", "desc": "Plataforma con cifras gigantes de jugadores."},
                {"nombre": "GTA V / GTA Online", "imagen": "img/comunidades/supervivencia/gtav.jpg", "desc": "Impulsado por el hype de GTA VI."},
                {"nombre": "Palworld", "imagen": "img/comunidades/shooters/palworld.jpg", "desc": "Pokemon con armas que conquisto el mundo."},
                {"nombre": "ARK: Survival Evolved", "imagen": "img/comunidades/shooters/ark.jpg", "desc": "Dinosaurios, supervivencia y construccion epica."},
                {"nombre": "Rust", "imagen": "img/comunidades/shooters/rust.jpg", "desc": "Supervivencia hardcore con comunidad intensa."},
                {"nombre": "Terraria", "imagen": "img/comunidades/shooters/terraria.jpg", "desc": "Sandbox 2D con contenido infinito."},
                {"nombre": "Valheim", "imagen": "img/comunidades/shooters/valheim.jpg", "desc": "Supervivencia vikinga que enamoro a todos."},
                {"nombre": "No Man's Sky", "imagen": "img/comunidades/shooters/nms.jpg", "desc": "Exploracion espacial sin limites."},
                {"nombre": "Red Dead Redemption 2", "imagen": "img/comunidades/shooters/rdr2.jpg", "desc": "El oeste salvaje con el mejor mundo abierto."},
                {"nombre": "Cyberpunk 2077", "imagen": "img/comunidades/shooters/cyberpunk.jpg", "desc": "RPG futurista con comunidad enorme."},
                {"nombre": "Sea of Thieves", "imagen": "img/comunidades/shooters/sot.jpg", "desc": "Aventuras pirata cooperativas."},
                {"nombre": "The Forest", "imagen": "img/comunidades/shooters/forest.jpg", "desc": "Supervivencia y terror en una isla."},
            ]
        },
        {
            "slug": "party-sports",
            "titulo": "Fiebre Global",
            "icono": "fa-futbol",
            "color": "#ec4899",
            "descripcion": "Deportes, party games y cooperativo. Diversion para todos.",
            "juegos": [
                {"nombre": "EA Sports FC 26", "imagen": "img/comunidades/shooters/eafc26.jpg", "desc": "El futbol sigue siendo de lo mas jugado."},
                {"nombre": "Rocket League", "imagen": "img/comunidades/shooters/rocket.jpg", "desc": "Futbol con coches. Simple y adictivo."},
                {"nombre": "Helldivers 2", "imagen": "img/comunidades/shooters/helldivers2.jpg", "desc": "Cooperativo con picos masivos de jugadores."},
                {"nombre": "Among Us", "imagen": "img/comunidades/shooters/amongus.jpg", "desc": "El party game que nunca muere."},
                {"nombre": "Dead by Daylight", "imagen": "img/comunidades/shooters/dbd.jpg", "desc": "Asimetrico de terror. Comunidad enorme."},
                {"nombre": "Phasmophobia", "imagen": "img/comunidades/shooters/phasmo.jpg", "desc": "Caza fantasmas cooperativa."},
                {"nombre": "Lethal Company", "imagen": "img/comunidades/shooters/lethal.jpg", "desc": "Cooperativo de terror que exploto en Twitch."},
                {"nombre": "Brawlhalla", "imagen": "img/comunidades/shooters/brawlhalla.jpg", "desc": "Plataformas de lucha gratuito."},
                {"nombre": "Street Fighter 6", "imagen": "img/comunidades/shooters/sf6.jpg", "desc": "El rey de los fighting games."},
                {"nombre": "Tekken 8", "imagen": "img/comunidades/shooters/tekken8.jpg", "desc": "Peleas 3D con comunidad competitiva."},
                {"nombre": "Mario Kart 8 Deluxe", "imagen": "img/comunidades/shooters/mk8.jpg", "desc": "Carreras arcade multijugador."},
                {"nombre": "Gran Turismo 7", "imagen": "img/comunidades/shooters/gt7.jpg", "desc": "El simulador de carreras definitivo."},
                {"nombre": "Forza Horizon 5", "imagen": "img/comunidades/shooters/fh5.jpg", "desc": "Mundo abierto sobre ruedas."},
            ]
        },
    ]


def get_categories_with_images(url_for_func):
    """Returns categories with resolved image URLs using Flask's url_for.

    Both explorar and comunidades routes call this so image changes
    are reflected in both sections automatically.
    """
    cats = get_game_categories()
    for cat in cats:
        for juego in cat['juegos']:
            juego['imagen'] = url_for_func('static', filename=juego['imagen'])
    return cats


def get_comunidades_categories(url_for_func):
    """Same categories but with distinct titles for the comunidades page."""
    cats = get_game_categories()
    titulos = {
        "shooters": "Zona de Fuego",
        "battle-royale": "Supervivencia Total",
        "moba-rpg": "Aventura Sin Limites",
        "sandbox": "Libertad Creativa",
        "party-sports": "Diversion en Grupo",
    }
    for cat in cats:
        cat['titulo'] = titulos.get(cat['slug'], cat['titulo'])
        for juego in cat['juegos']:
            juego['imagen'] = url_for_func('static', filename=juego['imagen'])
    return cats
