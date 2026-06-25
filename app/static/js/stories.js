window.RIFTZONE_STORIES = window.RIFTZONE_STORIES || {};

function switchStoryTab(tab) {
    document.querySelectorAll('.story-tab').forEach(function(t) { t.classList.remove('active'); });
    var tabBtn = document.querySelector('.story-tab[data-tab="' + tab + '"]');
    if (tabBtn) tabBtn.classList.add('active');
    document.getElementById('story-tipo-input').value = tab;
    document.getElementById('story-image-tab').style.display = tab === 'image' ? '' : 'none';
    var videoTab = document.getElementById('story-video-tab');
    if (videoTab) videoTab.style.display = tab === 'video' ? '' : 'none';
    document.getElementById('story-texto-tab').style.display = tab === 'texto' ? '' : 'none';
}

function selectStoryColor(el) {
    document.querySelectorAll('.story-color-opt').forEach(function(c) { c.classList.remove('selected'); });
    el.classList.add('selected');
    document.getElementById('story-color-input').value = el.dataset.color;
}

(function() {
    'use strict';

    var STORY_GRADIENTS = {
        '#7C3AED': ['#7C3AED', '#A78BFA', '#4C1D95'],
        '#FF2D95': ['#FF2D95', '#FF6B9D', '#B91C6B'],
        '#22D3EE': ['#22D3EE', '#67E8F9', '#0E7490'],
        '#34D399': ['#34D399', '#6EE7B7', '#047857'],
        '#FBBF24': ['#FBBF24', '#FCD34D', '#B45309'],
        '#F87171': ['#F87171', '#FCA5A5', '#B91C1C'],
        '#1E1E32': ['#1E1E32', '#37306B', '#0D0B1A'],
        '#0D0B1A': ['#0D0B1A', '#1E1E32', '#000000'],
    };
    var FALLBACK_GRADIENTS = [
        ['#7C3AED', '#A78BFA', '#4C1D95'],
        ['#FF2D95', '#FF6B9D', '#B91C6B'],
        ['#22D3EE', '#67E8F9', '#0E7490'],
        ['#34D399', '#6EE7B7', '#047857'],
        ['#FBBF24', '#FCD34D', '#B45309'],
        ['#F87171', '#FCA5A5', '#B91C1C'],
    ];
    var FLOATING_EMOJIS = ['❤️', '🔥', '💜', '✨', '💯', '🎮', '🌟', '💕'];

    function getStoryGradient(color) {
        if (STORY_GRADIENTS[color]) return STORY_GRADIENTS[color];
        var hash = 0;
        for (var i = 0; i < color.length; i++) { hash = color.charCodeAt(i) + ((hash << 5) - hash); }
        return FALLBACK_GRADIENTS[Math.abs(hash) % FALLBACK_GRADIENTS.length];
    }

    var state = {
        users: [],
        currentUserIndex: 0,
        currentStoryIndex: 0,
        isPlaying: false,
        timer: null,
        likedStories: {}
    };

    function loadFeed() {
        fetch('/historias/feed')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                state.users = data;
                renderBubbles(data);
                initStoryRings();
            })
            .catch(function() {});
    }

    function renderBubbles(users) {
        var container = document.getElementById('stories-container');
        if (!container) return;
        var html = '';
        if (window.RIFTZONE_CURRENT_USER) {
            html += '<div class="story-item" onclick="RIFTZONE_STORIES.openCreator()">' +
                '<div class="story-avatar-wrap" style="padding:0;background:rgba(255,255,255,0.06);border:2px dashed rgba(167,139,250,0.2)">' +
                '<img src="' + escapeHtml(window.RIFTZONE_CURRENT_USER.avatar) + '" alt="Tu historia" style="border-color:transparent;">' +
                '<div class="story-plus-badge"><i class="fas fa-plus"></i></div></div>' +
                '<span class="story-label">Crear historia</span></div>';
        }
        users.forEach(function(u) {
            var userIdx = users.indexOf(u);
            var avatarClass = 'story-avatar-wrap';
            if (u.tiene_no_vistas) avatarClass += ' story-unseen';
            html += '<div class="story-item" onclick="RIFTZONE_STORIES.openViewer(' + userIdx + ')" data-user="' + escapeHtml(u.username) + '">' +
                '<div class="' + avatarClass + '">' +
                '<img src="' + escapeHtml(u.avatar) + '" alt="' + escapeHtml(u.nombre) + '">' +
                '</div><span class="story-label">' + escapeHtml(u.username) + '</span></div>';
        });
        container.innerHTML = html;
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    RIFTZONE_STORIES.openCreator = function() {
        var overlay = document.getElementById('story-creator-overlay');
        if (overlay) overlay.style.display = 'flex';
    };

    RIFTZONE_STORIES.closeCreator = function() {
        var overlay = document.getElementById('story-creator-overlay');
        if (overlay) overlay.style.display = 'none';
    };

    RIFTZONE_STORIES.previewImage = function(input) {
        var preview = document.getElementById('story-preview-img');
        var placeholder = document.getElementById('story-preview-placeholder');
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
                if (placeholder) placeholder.style.display = 'none';
            };
            reader.readAsDataURL(input.files[0]);
        }
    };

    RIFTZONE_STORIES.previewVideo = function(input) {
        var preview = document.getElementById('story-video-preview');
        var placeholder = document.getElementById('story-video-placeholder');
        if (input.files && input.files[0]) {
            var url = URL.createObjectURL(input.files[0]);
            preview.src = url;
            preview.style.display = 'block';
            if (placeholder) placeholder.style.display = 'none';
        }
    };

    RIFTZONE_STORIES.submitStory = function() {
        var form = document.getElementById('story-create-form');
        var formData = new FormData(form);
        var btn = form.querySelector('button[type="button"]');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publicando...';
        fetch(form.action, { method: 'POST', body: formData })
            .then(function(r) { return r.json(); })
            .then(function(resp) {
                if (resp.success) {
                    RIFTZONE_STORIES.closeCreator();
                    loadFeed();
                    showToast('Historia publicada', 'success');
                } else {
                    alert(resp.message || 'Error al crear historia.');
                }
            })
            .catch(function() { alert('Error de conexión.'); })
            .finally(function() { btn.disabled = false; btn.innerHTML = '<i class="fas fa-plus"></i> Publicar'; });
    };

    RIFTZONE_STORIES.openViewer = function(userIndex) {
        state.currentUserIndex = userIndex;
        state.currentStoryIndex = 0;
        var user = state.users[userIndex];
        if (!user || !user.historias || user.historias.length === 0) return;
        var viewer = document.getElementById('story-viewer');
        viewer.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        showCurrentStory();
    };

    RIFTZONE_STORIES.navPrev = function(e) {
        if (e) e.stopPropagation();
        prevStory();
    };
    RIFTZONE_STORIES.navNext = function(e) {
        if (e) e.stopPropagation();
        nextStory();
    };

    RIFTZONE_STORIES.closeViewer = function() {
        stopAutoAdvance();
        var viewer = document.getElementById('story-viewer');
        viewer.style.display = 'none';
        document.body.style.overflow = '';
    };

    RIFTZONE_STORIES.toggleLike = function() {
        var user = state.users[state.currentUserIndex];
        if (!user) return;
        var story = user.historias[state.currentStoryIndex];
        if (!story) return;
        var liked = !story.liked_by_me;
        story.liked_by_me = liked;
        story.total_likes += liked ? 1 : -1;
        fetch('/historias/' + story.id + '/like', { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } }).catch(function() {});
        updateLikeButton(story);
        if (liked) spawnFloatingEmoji('❤️');
    };

    RIFTZONE_STORIES.sendReply = function() {
        var user = state.users[state.currentUserIndex];
        if (!user) return;
        var story = user.historias[state.currentStoryIndex];
        if (!story) return;
        var input = document.getElementById('story-reply-input');
        var mensaje = (input.value || '').trim();
        if (!mensaje) return;
        fetch('/historias/' + story.id + '/responder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ mensaje: mensaje })
        }).then(function(r) { return r.json(); }).then(function(resp) {
            if (resp.success) {
                showToast('Respuesta enviada', 'success');
                input.value = '';
            } else {
                showToast(resp.message || 'Error', 'error');
            }
        }).catch(function() { showToast('Error de conexión', 'error'); });
    };

    RIFTZONE_STORIES.toggleMenu = function(e) {
        if (e) e.stopPropagation();
        var overlay = document.getElementById('story-menu-overlay');
        var menu = document.getElementById('story-context-menu');
        if (menu.classList.contains('open')) {
            RIFTZONE_STORIES.closeMenu();
            return;
        }
        var user = state.users[state.currentUserIndex];
        var story = user ? user.historias[state.currentStoryIndex] : null;
        if (!story) return;
        var isOwner = user && window.RIFTZONE_CURRENT_USER && user.id_usuario === window.RIFTZONE_CURRENT_USER.id;
        menu.innerHTML = buildMenuHTML(story, isOwner);
        menu.classList.add('open');
        if (overlay) overlay.classList.add('open');
    };

    RIFTZONE_STORIES.closeMenu = function() {
        var menu = document.getElementById('story-context-menu');
        var overlay = document.getElementById('story-menu-overlay');
        menu.classList.remove('open');
        if (overlay) overlay.classList.remove('open');
    };

    RIFTZONE_STORIES.menuAction = function(action, storyId) {
        RIFTZONE_STORIES.closeMenu();
        var user = state.users[state.currentUserIndex];
        var story = user ? user.historias[state.currentStoryIndex] : null;
        var actions = {
            compartir: function() {
                if (navigator.share) {
                    navigator.share({ title: 'RiftZone - Historia', url: window.location.origin + '/historias/' + storyId }).catch(function() {});
                } else {
                    navigator.clipboard.writeText(window.location.origin + '/historias/' + storyId).then(function() {
                        showToast('Enlace copiado', 'success');
                    });
                }
            },
            copiar_enlace: function() {
                navigator.clipboard.writeText(window.location.origin + '/historias/' + storyId).then(function() {
                    showToast('Enlace copiado al portapapeles', 'success');
                });
            },
            responder: function() {
                document.getElementById('story-reply-input').focus();
            },
            silenciar: function() {
                fetch('/historias/' + storyId + '/silenciar', { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } })
                    .then(function(r) { return r.json(); }).then(function(d) { showToast(d.message || 'Usuario silenciado', 'success'); })
                    .catch(function() { showToast('Error', 'error'); });
            },
            ocultar: function() {
                showToast('Historia oculta. No volverás a ver historias de este usuario por 24h.', 'info');
            },
            reportar: function() {
                fetch('/historias/' + storyId + '/reportar', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() }, body: JSON.stringify({ motivo: 'inapropiado' }) })
                    .then(function(r) { return r.json(); }).then(function(d) { showToast(d.message || 'Historia reportada', 'success'); })
                    .catch(function() { showToast('Error', 'error'); });
            },
            bloquear: function() {
                fetch('/historias/' + storyId + '/bloquear', { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } })
                    .then(function(r) { return r.json(); }).then(function(d) { showToast(d.message || 'Usuario bloqueado', 'success'); })
                    .catch(function() { showToast('Error', 'error'); });
            },
            eliminar: function() {
                if (!confirm('¿Eliminar esta historia?')) return;
                fetch('/historias/eliminar/' + storyId, { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } })
                    .then(function(r) { return r.json(); }).then(function(d) {
                        if (d.success) { showToast('Historia eliminada', 'success'); RIFTZONE_STORIES.closeViewer(); loadFeed(); }
                        else { showToast(d.message || 'Error', 'error'); }
                    }).catch(function() { showToast('Error', 'error'); });
            },
            destacar: function() {
                fetch('/historias/' + storyId + '/destacar', { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } })
                    .then(function(r) { return r.json(); }).then(function(d) { showToast(d.destacada ? 'Historia destacada' : 'Destacado quitado', 'success'); })
                    .catch(function() { showToast('Error', 'error'); });
            },
            guardar: function() {
                fetch('/historias/' + storyId + '/guardar', { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } })
                    .then(function(r) { return r.json(); }).then(function(d) { showToast(d.guardado ? 'Historia guardada' : 'Guardado quitado', 'success'); })
                    .catch(function() { showToast('Error', 'error'); });
            },
            estadisticas: function() {
                RIFTZONE_STORIES.openStats();
            },
            privacidad: function(val) {
                var story = getCurrentStory();
                if (!story) return;
                fetch('/historias/' + story.id + '/privacidad', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() }, body: JSON.stringify({ privacidad: val }) })
                    .then(function(r) { return r.json(); }).then(function(d) {
                        if (d.success) showToast('Privacidad cambiada a ' + d.privacidad, 'success');
                    }).catch(function() { showToast('Error', 'error'); });
            }
        };
        if (actions[action]) actions[action]();
    };

    function getCurrentStory() {
        var user = state.users[state.currentUserIndex];
        if (!user) return null;
        return user.historias[state.currentStoryIndex] || null;
    }

    function buildMenuHTML(story, isOwner) {
        var items = [];
        if (isOwner) {
            items.push({ icon: 'fa-chart-bar', label: 'Estadísticas', action: 'estadisticas' });
            items.push({ icon: 'fa-star', label: 'Destacar historia', action: 'destacar' });
            items.push({ icon: 'fa-bookmark', label: 'Guardar historia', action: 'guardar' });
            items.push({ type: 'divider' });
            items.push({ icon: 'fa-lock', label: 'Privacidad: Pública', action: 'privacidad_publico', sub: true });
            items.push({ icon: 'fa-users', label: 'Solo seguidores', action: 'privacidad_seguidores', sub: true });
            items.push({ icon: 'fa-user-friends', label: 'Solo amigos', action: 'privacidad_amigos', sub: true });
            items.push({ icon: 'fa-lock', label: 'Privada', action: 'privacidad_privado', sub: true });
            items.push({ type: 'divider' });
            items.push({ icon: 'fa-trash-alt', label: 'Eliminar historia', action: 'eliminar', danger: true });
        } else {
            items.push({ icon: 'fa-share-alt', label: 'Compartir historia', action: 'compartir' });
            items.push({ icon: 'fa-link', label: 'Copiar enlace', action: 'copiar_enlace' });
            items.push({ icon: 'fa-reply', label: 'Responder', action: 'responder' });
            items.push({ type: 'divider' });
            items.push({ icon: 'fa-volume-mute', label: 'Silenciar usuario', action: 'silenciar' });
            items.push({ icon: 'fa-eye-slash', label: 'Ocultar historia', action: 'ocultar' });
            items.push({ icon: 'fa-flag', label: 'Reportar', action: 'reportar' });
            items.push({ icon: 'fa-ban', label: 'Bloquear usuario', action: 'bloquear', danger: true });
        }
        var html = '<div class="story-menu-header"><span>Opciones</span><button onclick="RIFTZONE_STORIES.closeMenu()"><i class="fas fa-times"></i></button></div><div class="story-menu-body">';
        items.forEach(function(item) {
            if (item.type === 'divider') {
                html += '<div class="story-menu-divider"></div>';
            } else if (item.sub) {
                var privVal = item.action.replace('privacidad_', '');
                html += '<button class="story-menu-item story-menu-sub" onclick="RIFTZONE_STORIES.menuAction(\'privacidad\', \'' + privVal + '\')">';
                html += '<i class="fas ' + item.icon + '"></i> <span>' + item.label + '</span></button>';
            } else {
                html += '<button class="story-menu-item' + (item.danger ? ' story-menu-danger' : '') + '" onclick="RIFTZONE_STORIES.menuAction(\'' + item.action + '\', ' + story.id + ')">';
                html += '<i class="fas ' + item.icon + '"></i> <span>' + item.label + '</span></button>';
            }
        });
        html += '</div>';
        return html;
    }

    function initStoryRings() {
        fetch('/historias/usuarios_activos')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.user_ids || !data.user_ids.length) return;
                var ids = new Set(data.user_ids);
                document.querySelectorAll('.avatar-frame, .friend-avatar-wrap, .post-avatar-wrap, .comment-avatar-wrap, [data-user-id]').forEach(function(el) {
                    var uid = parseInt(el.getAttribute('data-user-id'));
                    if (ids.has(uid)) el.classList.add('has-story');
                });
                document.querySelectorAll('img[alt], .avatar-img').forEach(function(img) {
                    var wrap = img.closest('.avatar-frame, .friend-avatar-wrap, [data-user-id]');
                    if (wrap && ids.has(parseInt(wrap.getAttribute('data-user-id')))) {
                        wrap.classList.add('has-story');
                    }
                });
            })
            .catch(function() {});
    }

    RIFTZONE_STORIES.openStats = function() {
        var user = state.users[state.currentUserIndex];
        if (!user) return;
        var story = user.historias[state.currentStoryIndex];
        if (!story) return;
        fetch('/historias/' + story.id + '/stats')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.success) return;
                var modal = document.getElementById('story-stats-modal');
                var list = modal.querySelector('.story-stats-list');
                var html = '<div class="story-stats-summary">' +
                    '<span><i class="fas fa-eye"></i> ' + data.total_vistas + ' vistas</span>' +
                    '<span><i class="fas fa-heart"></i> ' + data.total_likes + ' likes</span>';
                for (var e in data.reacciones) {
                    html += '<span>' + e + ' ' + data.reacciones[e] + '</span>';
                }
                html += '</div>';
                html += '<div class="story-stats-users"><h4>Visto por</h4>';
                if (data.usuarios_vieron && data.usuarios_vieron.length) {
                    data.usuarios_vieron.forEach(function(v) {
                        html += '<div class="story-stats-user"><img src="' + escapeHtml(v.avatar) + '" alt=""> <span>' + escapeHtml(v.username) + '</span></div>';
                    });
                } else {
                    html += '<p class="text-muted">Nadie ha visto esta historia aún</p>';
                }
                html += '</div>';
                list.innerHTML = html;
                modal.classList.add('is-open');
            })
            .catch(function() {});
    };

    function updateReactionDisplay(story) {
        var btn = document.querySelector('.story-emoji-btn');
        if (!btn) return;
        if (story.mi_reaccion) {
            btn.textContent = story.mi_reaccion;
            btn.classList.add('has-reaction');
        } else {
            btn.innerHTML = '<i class="far fa-smile-wink"></i>';
            btn.classList.remove('has-reaction');
        }
    }

    function toggleEmojiPanel() {
        var panel = document.getElementById('story-emoji-panel');
        if (panel) panel.classList.toggle('open');
    }

    function selectEmoji(emoji) {
        var user = state.users[state.currentUserIndex];
        if (!user) return;
        var story = user.historias[state.currentStoryIndex];
        if (!story) return;
        story.mi_reaccion = emoji;
        fetch('/historias/' + story.id + '/reaccion', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() }, body: JSON.stringify({ emoji: emoji }) }).catch(function() {});
        updateReactionDisplay(story);
        var panel = document.getElementById('story-emoji-panel');
        if (panel) panel.classList.remove('open');
        spawnFloatingEmoji(emoji);
    }

    function updateLikeButton(story) {
        var btn = document.querySelector('.story-like-btn');
        if (!btn) return;
        if (story.liked_by_me) {
            btn.classList.add('liked');
            btn.querySelector('i').className = 'fas fa-heart';
        } else {
            btn.classList.remove('liked');
            btn.querySelector('i').className = 'far fa-heart';
        }
        var count = btn.querySelector('.story-like-count');
        if (count) count.textContent = story.total_likes || '';
    }

    function registerView(storyId) {
        fetch('/historias/' + storyId + '/vista', { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } }).catch(function() {});
    }

    function spawnFloatingEmoji(emoji) {
        var container = document.querySelector('.story-viewer-content');
        if (!container) return;
        var el = document.createElement('div');
        el.className = 'story-floating-emoji';
        el.textContent = emoji || FLOATING_EMOJIS[Math.floor(Math.random() * FLOATING_EMOJIS.length)];
        var startX = 30 + Math.random() * 40;
        el.style.left = startX + '%';
        container.appendChild(el);
        requestAnimationFrame(function() {
            el.classList.add('animate');
        });
        setTimeout(function() { el.remove(); }, 2000);
    }

    function emojiRain(count) {
        var container = document.querySelector('.story-viewer-content');
        if (!container) return;
        for (var i = 0; i < count; i++) {
            (function(delay) {
                setTimeout(function() {
                    var el = document.createElement('div');
                    el.className = 'story-floating-emoji story-emoji-rain';
                    el.textContent = FLOATING_EMOJIS[Math.floor(Math.random() * FLOATING_EMOJIS.length)];
                    el.style.left = Math.random() * 100 + '%';
                    el.style.animationDuration = (1.5 + Math.random()) + 's';
                    container.appendChild(el);
                    setTimeout(function() { el.remove(); }, 3000);
                }, delay);
            })(i * 80);
        }
    }

    function showCurrentStory() {
        var user = state.users[state.currentUserIndex];
        if (!user || !user.historias || user.historias.length === 0) {
            RIFTZONE_STORIES.closeViewer();
            return;
        }
        var story = user.historias[state.currentStoryIndex];
        if (!story) {
            nextUser();
            return;
        }

        var viewer = document.getElementById('story-viewer');
        viewer.querySelector('.story-viewer-user .story-viewer-avatar').src = user.avatar;
        viewer.querySelector('.story-viewer-user .story-viewer-name').textContent = user.nombre;
        viewer.querySelector('.story-viewer-user .story-viewer-time').textContent = timeAgo(story.created_at);
        viewer.querySelector('.story-viewer-user .story-viewer-counter').textContent = (state.currentStoryIndex + 1) + ' / ' + user.historias.length;

        var content = viewer.querySelector('.story-viewer-content');
        content.innerHTML = '';

        if (story.tipo === 'image' && story.archivo_url) {
            var img = document.createElement('img');
            img.src = story.archivo_url;
            img.className = 'story-media';
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s';
            img.onload = function() { img.style.opacity = '1'; startAutoAdvance(); registerView(story.id); };
            img.onerror = function() { startAutoAdvance(); };
            content.appendChild(img);
        } else if (story.tipo === 'texto') {
            var wrapper = document.createElement('div');
            wrapper.className = 'story-text-content';
            var baseColor = story.color_fondo || '#7C3AED';
            var grad = getStoryGradient(baseColor);
            wrapper.style.background = 'linear-gradient(135deg, ' + grad[0] + ', ' + grad[1] + ', ' + grad[2] + ')';
            wrapper.style.backgroundSize = '200% 200%';
            wrapper.style.animation = 'storyGradAnim 6s ease infinite';
            var inner = document.createElement('div');
            inner.className = 'story-text-content-inner';
            inner.textContent = story.caption || '';
            wrapper.appendChild(inner);
            content.appendChild(wrapper);
            startAutoAdvance();
            registerView(story.id);
        } else if (story.tipo === 'video' && story.archivo_url) {
            var video = document.createElement('video');
            video.src = story.archivo_url;
            video.className = 'story-media';
            video.autoplay = true;
            video.muted = false;
            video.playsInline = true;
            video.style.opacity = '0';
            video.style.transition = 'opacity 0.3s';
            video.onloadedmetadata = function() {
                video.style.opacity = '1';
                var duration = video.duration * 1000;
                startAutoAdvance(duration);
                registerView(story.id);
            };
            video.onerror = function() { startAutoAdvance(); };
            video.onended = function() { nextStory(); };
            content.appendChild(video);
        }

        updateLikeButton(story);
        updateReactionDisplay(story);
        renderProgressBars();
        updateProgress();

        var replyInput = document.getElementById('story-reply-input');
        if (replyInput) replyInput.value = '';
        var emojiPanel = document.getElementById('story-emoji-panel');
        if (emojiPanel) { emojiPanel.classList.remove('open'); }
    }

    function renderProgressBars() {
        var user = state.users[state.currentUserIndex];
        if (!user) return;
        var container = document.getElementById('story-progress-bars');
        container.innerHTML = '';
        user.historias.forEach(function(_, i) {
            var bar = document.createElement('div');
            bar.className = 'story-progress-bar';
            if (i < state.currentStoryIndex) bar.classList.add('completed');
            else if (i === state.currentStoryIndex) bar.classList.add('active');
            var fill = document.createElement('div');
            fill.className = 'story-progress-fill';
            bar.appendChild(fill);
            container.appendChild(bar);
        });
    }

    function updateProgress() {
        var bars = document.querySelectorAll('#story-progress-bars .story-progress-bar');
        bars.forEach(function(bar, i) {
            bar.classList.remove('completed', 'active');
            bar.style.removeProperty('--progress');
            if (i < state.currentStoryIndex) bar.classList.add('completed');
            else if (i === state.currentStoryIndex) bar.classList.add('active');
        });
    }

    function startAutoAdvance(duration) {
        stopAutoAdvance();
        var user = state.users[state.currentUserIndex];
        if (!user) return;
        var story = user.historias[state.currentStoryIndex];
        if (!story) return;
        var tiempo = duration || 10000;

        var active = document.querySelector('#story-progress-bars .story-progress-bar.active');
        if (active) {
            var fill = active.querySelector('.story-progress-fill');
            if (fill) {
                fill.style.transition = 'none';
                fill.style.width = '0%';
                requestAnimationFrame(function() {
                    fill.style.transition = 'width ' + (tiempo / 1000) + 's linear';
                    fill.style.width = '100%';
                });
            }
        }

        state.isPlaying = true;
        state.timer = setTimeout(function() { nextStory(); }, tiempo);
    }

    function stopAutoAdvance() {
        state.isPlaying = false;
        if (state.timer) { clearTimeout(state.timer); state.timer = null; }
    }

    function nextStory() {
        stopAutoAdvance();
        var user = state.users[state.currentUserIndex];
        if (!user) return;
        if (state.currentStoryIndex < user.historias.length - 1) {
            state.currentStoryIndex++;
            showCurrentStory();
        } else {
            nextUser();
        }
    }

    function prevStory() {
        stopAutoAdvance();
        if (state.currentStoryIndex > 0) {
            state.currentStoryIndex--;
            showCurrentStory();
        } else {
            prevUser();
        }
    }

    function nextUser() {
        if (state.currentUserIndex < state.users.length - 1) {
            state.currentUserIndex++;
            state.currentStoryIndex = 0;
            showCurrentStory();
        } else {
            RIFTZONE_STORIES.closeViewer();
        }
    }

    function prevUser() {
        if (state.currentUserIndex > 0) {
            state.currentUserIndex--;
            state.currentStoryIndex = 0;
            showCurrentStory();
        }
    }

    function timeAgo(dateStr) {
        if (!dateStr) return '';
        var now = new Date();
        var date = new Date(dateStr);
        var diff = Math.floor((now - date) / 1000);
        if (diff < 60) return 'hace unos segundos';
        if (diff < 3600) return 'hace ' + Math.floor(diff / 60) + ' min';
        if (diff < 86400) return 'hace ' + Math.floor(diff / 3600) + ' h';
        return 'hace ' + Math.floor(diff / 86400) + ' d';
    }

    function getCSRFToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    document.addEventListener('DOMContentLoaded', function() {
        loadFeed();

        var viewer = document.getElementById('story-viewer');
        if (!viewer) return;

        viewer.addEventListener('click', function(e) {
            if (e.target === viewer || e.target.closest('.story-viewer-close')) {
                RIFTZONE_STORIES.closeViewer();
            }
        });

        viewer.addEventListener('touchstart', function(e) {
            var touch = e.touches[0];
            viewer._touchStartX = touch.clientX;
            viewer._touchStartY = touch.clientY;
            viewer._touchTime = Date.now();
        }, { passive: true });

        viewer.addEventListener('touchend', function(e) {
            if (!viewer._touchStartX) return;
            var dx = e.changedTouches[0].clientX - viewer._touchStartX;
            var dy = e.changedTouches[0].clientY - viewer._touchStartY;
            var dt = Date.now() - viewer._touchTime;
            if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) && dt < 300) {
                if (dx < 0) nextStory();
                else prevStory();
            } else if (Math.abs(dy) > 100 && Math.abs(dy) > Math.abs(dx) && dy < 0 && dt < 300) {
            }
            viewer._touchStartX = null;
        }, { passive: true });

        var lastTap = 0;
        viewer.addEventListener('click', function(e) {
            if (e.target.closest('.story-viewer-header') || e.target.closest('.story-viewer-footer') || e.target.closest('.story-like-btn') || e.target.closest('.story-nav-hint')) return;
            var now = Date.now();
            if (now - lastTap < 400) {
                RIFTZONE_STORIES.toggleLike();
            }
            lastTap = now;
        });

        document.addEventListener('keydown', function(e) {
            if (viewer.style.display !== 'flex') return;
            if (e.key === 'Escape') { RIFTZONE_STORIES.closeViewer(); }
            else if (e.key === 'ArrowRight') { nextStory(); }
            else if (e.key === 'ArrowLeft') { prevStory(); }
            else if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); RIFTZONE_STORIES.toggleLike(); }
        });

        var replyInput = document.getElementById('story-reply-input');
        if (replyInput) {
            replyInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    RIFTZONE_STORIES.sendReply();
                }
            });
        }

        initStoryRings();
    });
})();
