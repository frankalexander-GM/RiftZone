import sys, time, random
sys.path.insert(0, '.')

from app.factories.app_factory import create_app, db
from app.models.usuario import Usuario
from app.services.chat_service import ChatService
from flask_login import login_user

app = create_app()

MENSAJES = [
    "🔥 ¡Hay fuego en el chat hoy!",
    "🎮 ¿Alguien para una ranked?",
    "💬 99+ mensajes y nadie dice nada... ah no",
    "🚀 RiftZone está que arde esta noche",
    "⚡ ¿Ya vieron las nuevas misiones?",
    "👀 yo mirando el chat sin escribir nada...",
    "🎯 10 XP por mensaje, ¡aprovechen!",
    "💎 La comunidad está imparable",
    "🌊 Este chat fluye como lava",
    "🤖 bip bop, mensaje automático... pero con cariño",
    "🔥 @everyone ¿dónde están todos?",
    "📢 ¡Sigan así y llegarán a Inmortales!",
    "✨ Cada mensaje los acerca al próximo rango",
    "⚔️ Nivel 60 aquí, ¿alguien me alcanza?",
    "🎉 ¿1000 mensajes? Esto recién empieza",
    "💪 La racha de hoy está fuerte",
    "🌌 El Vórtice los llama... escriban algo",
    "🛡️ Comunidad unida, comunidad fuerte",
    "🎵 esto podría ser una playlist del chat",
    "👑 Ser Inmortal no es fácil, pero vale la pena",
    "🔥 5 mensajes y subo de nivel... okay no",
    "💬 Este chat es mi segundo hogar",
    "⚡ Activen ese @ para mencionar a alguien",
    "🎮 ¿Main support o carry? Discutamos",
    "🌟 10 horas después... y el chat sigue activo",
    "🚀 Despegue inminente del chat global",
    "💎 RiftZone > cualquier otro lado",
    "👀 cuando el chat está quieto pero tú vigilas",
    "🎯 Apunten a la racha diaria, no falla",
    "🔥 Esto es más adictivo que las misiones",
    "📢 ¡Récord de mensajes hoy, equipo!",
    "⚔️ Nivel 60+, chat activo, ¿qué más quieren?",
    "✨ La comunidad es lo que hace grande a RiftZone",
    "💪 Hoy es buen día para escribir en el chat",
    "🌊 El chat está vivo... gracias a ustedes",
    "🎮 ¿Alguien juega algo bueno hoy? Recomienden",
    "🔥 Este hilo nunca muere",
    "⚡ Cada @ es una invitación a la charla",
    "💬 Mensaje #?? + 1 y contando",
    "🌟 Cuando el chat global está prendido, todo fluye",
]

BOT_USERNAME = 'RiftBot'

with app.app_context():
    bot = Usuario.query.filter_by(username=BOT_USERNAME).first()
    if not bot:
        print('Bot no encontrado')
        sys.exit(1)

    service = ChatService()
    print(f'Bot {BOT_USERNAME} iniciado (ID: {bot.id_usuario})')

    idx = 0
    while True:
        try:
            msg = MENSAJES[idx % len(MENSAJES)]
            service.enviar_mensaje(bot.id_usuario, msg, bot)
            print(f'[{time.strftime("%H:%M:%S")}] Bot envió: {msg}')
            idx += 1
        except Exception as e:
            print(f'Error: {e}')

        tiempo = random.randint(8, 20)
        time.sleep(tiempo)