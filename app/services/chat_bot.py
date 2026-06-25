import threading
import random
import time

BOT_MESSAGES = [
    "🎮 ¿Alguien quiere jugar algo hoy?",
    "🔥 Llevo 3 horas seguidas jugando, ¿y ustedes?",
    "💬 El mejor juego de la historia es... ¡debate!",
    "⚡ ¿Alguien probó el nuevo parche?",
    "🏆 Mañana torneo relámpago, ¿se apuntan?",
    "👾 Si ven a un tal 'NoobMaster69' por ahí, huyan.",
    "🎯 Mi aim está horrible hoy, ¿a alguien más le pasa?",
    "🕹️ ¿Juegos gratis que recomienden esta semana?",
    "🌟 Recuerden hidratarse entre partida y partida 💧",
    "💀 1v1 en Valorant, el que pierde invita la cena.",
    "🎲 ¿Alguien para un ranked? Necesito carry.",
    "🔥 Récord personal de kills hoy: 32!",
    "😱 Alguien más se quedó viendo el amanecer jugando?",
    "💪 El main character no se rinde nunca.",
    "🥷 Modo sigiloso: jefe llegó y minimicé la pantalla.",
]

class ChatBot:
    def __init__(self, bot_user_id=1):
        self.bot_user_id = bot_user_id
        self._running = False
        self._thread = None

    def start(self, app):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, args=(app,), daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self, app):
        while self._running:
            time.sleep(30)
            if not self._running:
                break
            try:
                with app.app_context():
                    from app.factories.service_factory import get_service_factory
                    from app.factories.app_factory import db
                    from app.models.chat import MensajeChat

                    mensaje = random.choice(BOT_MESSAGES)
                    msg = MensajeChat(
                        usuario_id=self.bot_user_id,
                        contenido=mensaje
                    )
                    db.session.add(msg)
                    db.session.commit()
            except Exception:
                import traceback
                traceback.print_exc()

chat_bot = ChatBot()
