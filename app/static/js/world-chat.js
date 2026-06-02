/**
 * Chat mundial (sidebar mini-chat y página /chat/global).
 */
(function () {
    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text == null ? '' : String(text);
        return div.innerHTML;
    }

    function renderMensaje(msg, mini) {
        const avatarSize = mini ? 24 : 40;
        const nameSize = mini ? 13 : 15;
        const textSize = mini ? 12 : 14;
        const gap = mini ? 8 : 16;
        const crown = mini
            ? '<i class="fas fa-crown" style="font-size: 10px; margin-left: 2px;"></i>'
            : '<i class="fas fa-crown" style="font-size: 12px; margin-left: 4px;"></i>';
        let nameColor = 'white';
        let nameShadow = 'none';
        if (msg.boost_color) {
            nameColor = msg.boost_color;
            nameShadow = `0 0 8px ${msg.boost_color}88`;
        } else if (msg.es_premium) {
            nameColor = '#FACC15';
            nameShadow = mini
                ? '0 0 5px rgba(250, 204, 21, 0.3)'
                : '0 0 5px rgba(250, 204, 21, 0.4)';
        }

        return `
            <div style="display:flex; gap:${gap}px;">
                <img src="${escapeHtml(msg.usuario_foto)}" alt="" style="width:${avatarSize}px; height:${avatarSize}px; border-radius:50%; object-fit:cover; flex-shrink:0;">
                <div style="flex:1; min-width:0;">
                    <div style="display:flex; align-items:baseline; gap:6px; flex-wrap:wrap;">
                        <strong style="color:${nameColor}; font-size:${nameSize}px; text-shadow:${nameShadow};">
                            ${escapeHtml(msg.usuario_nombre)}
                            ${msg.es_premium ? crown : ''}
                        </strong>
                        <span style="color:var(--text-muted); font-size:${mini ? 10 : 12}px;">${escapeHtml(msg.fecha_envio)}</span>
                    </div>
                    <p style="color:#d1d5db; margin-top:${mini ? 2 : 4}px; font-size:${textSize}px; line-height:1.4; word-break:break-word; margin-bottom:0;">
                        ${escapeHtml(msg.contenido)}
                    </p>
                </div>
            </div>`;
    }

    function initChat(options) {
        const container = document.getElementById(options.containerId);
        if (!container || !options.messagesUrl) return null;

        const form = options.formId ? document.getElementById(options.formId) : null;
        const input = options.inputId ? document.getElementById(options.inputId) : null;
        let isScrolledToBottom = true;
        let connected = false;

        container.addEventListener('scroll', () => {
            isScrolledToBottom =
                container.scrollHeight - container.clientHeight <= container.scrollTop + (options.mini ? 20 : 50);
        });

        function showStatus(html) {
            container.innerHTML = html;
        }

        async function cargarMensajes() {
            try {
                const res = await fetch(options.messagesUrl, {
                    credentials: 'same-origin',
                    headers: { Accept: 'application/json' },
                });
                const data = await res.json().catch(() => ({}));

                if (!res.ok || data.success === false) {
                    const err = data.error || 'No se pudo conectar al chat mundial.';
                    showStatus(
                        `<div style="text-align:center; color:var(--accent-magenta); font-size:12px; padding:12px;">
                            <i class="fas fa-exclamation-circle"></i> ${escapeHtml(err)}
                        </div>`
                    );
                    connected = false;
                    return;
                }

                connected = true;
                const mensajes = data.mensajes || [];
                if (mensajes.length === 0) {
                    showStatus(
                        `<div style="text-align:center; color:var(--text-muted); font-size:${options.mini ? 12 : 13}px; margin-top:12px;">
                            ¡Sé el primero en escribir!
                        </div>`
                    );
                } else {
                    container.innerHTML = '';
                    mensajes.forEach((msg) => {
                        container.insertAdjacentHTML('beforeend', renderMensaje(msg, options.mini));
                    });
                }

                if (isScrolledToBottom) {
                    container.scrollTop = container.scrollHeight;
                }
            } catch (e) {
                console.error('Chat mundial:', e);
                if (!connected) {
                    showStatus(
                        `<div style="text-align:center; color:var(--accent-magenta); font-size:12px; padding:12px;">
                            <i class="fas fa-wifi"></i> Sin conexión al chat. ¿Servidor encendido?
                        </div>`
                    );
                }
            }
        }

        if (form && input && options.sendUrl) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const contenido = input.value.trim();
                if (!contenido) return;

                input.value = '';
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.disabled = true;

                try {
                    const res = await fetch(options.sendUrl, {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken(),
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: JSON.stringify({ contenido }),
                    });
                    const data = await res.json().catch(() => ({}));
                    if (!res.ok) {
                        showToast(data.error || 'No se pudo enviar el mensaje.', 'error');
                        input.value = contenido;
                        return;
                    }
                    isScrolledToBottom = true;
                    await cargarMensajes();
                } catch (err) {
                    console.error(err);
                    showToast('Error de conexión al enviar.', 'error');
                    input.value = contenido;
                } finally {
                    if (submitBtn) submitBtn.disabled = false;
                }
            });
        }

        const interval = options.pollInterval || (options.mini ? 3000 : 2500);
        const intervalId = setInterval(cargarMensajes, interval);
        cargarMensajes();

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) clearInterval(intervalId);
            else intervalId = setInterval(cargarMensajes, interval);
        });

        return { reload: cargarMensajes };
    }

    document.addEventListener('DOMContentLoaded', () => {
        const cfg = window.RIFTZONE_CHAT;
        if (!cfg) return;

        if (cfg.mini) {
            initChat({
                containerId: 'mini-chat-messages',
                formId: 'mini-chat-form',
                inputId: 'mini-chat-input',
                messagesUrl: cfg.messagesUrl,
                sendUrl: cfg.sendUrl,
                mini: true,
                pollInterval: 3000,
            });
        }

        if (cfg.full) {
            initChat({
                containerId: 'chat-messages',
                formId: 'chat-form',
                inputId: 'chat-input',
                messagesUrl: cfg.messagesUrl,
                sendUrl: cfg.sendUrl,
                mini: false,
                pollInterval: 2500,
            });
        }
    });
})();
