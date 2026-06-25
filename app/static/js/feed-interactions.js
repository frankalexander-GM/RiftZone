(function () {
    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content');
        const input = document.querySelector('input[name="csrf_token"]');
        return input ? input.value : '';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function toggleLike(postId, btn) {
        if (!postId || !btn || btn.disabled) return;
        btn.disabled = true;
        fetch(`/jugador/like/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then(async (res) => {
                const data = await res.json().catch(() => ({}));
                if (!res.ok) throw new Error(data.message || 'No se pudo actualizar el like.');
                return data;
            })
            .then((data) => {
                if (!data.success) return;
                const countSpan = document.getElementById(`like-count-${postId}`);
                const icon = btn.querySelector('i');
                if (data.liked) {
                    btn.classList.add('liked');
                    if (icon) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                    }
                } else {
                    btn.classList.remove('liked');
                    if (icon) {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                    }
                }
                if (countSpan) countSpan.textContent = data.likes_count;
            })
            .catch((err) => {
                showToast(err.message || 'Error de conexión al dar like.', 'error');
            })
            .finally(() => {
                btn.disabled = false;
            });
    }

    function toggleComments(postId) {
        const section = document.getElementById(`comments-${postId}`);
        if (!section) return;
        const open = section.style.display !== 'block';
        section.style.display = open ? 'block' : 'none';
        if (open) {
            const input = section.querySelector('.comment-form input[name="contenido"]');
            if (input) input.focus();
        }
    }

    function appendComment(postId, comment) {
        const list = document.getElementById(`comments-list-${postId}`);
        if (!list || !comment) return;
        const empty = list.querySelector('.comments-empty');
        if (empty) empty.remove();
        const html = `
            <div class="comment" style="display:flex; gap:12px; margin-bottom:12px;">
                <img src="${escapeHtml(comment.foto)}" alt="" style="width:32px; height:32px; border-radius:50%; object-fit:cover;">
                <div class="comment-content" style="background:var(--bg-dark); padding:10px 12px; border-radius:var(--radius-md); flex:1;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; gap:8px;">
                        <span style="font-size:13px; font-weight:700;">${escapeHtml(comment.autor_nombre)}</span>
                        <span style="font-size:11px; color:var(--text-muted); flex-shrink:0;">${escapeHtml(comment.fecha)}</span>
                    </div>
                    <p style="font-size:13px; color:white; line-height:1.4; margin:0;">${escapeHtml(comment.contenido)}</p>
                </div>
            </div>`;
        list.insertAdjacentHTML('beforeend', html);
    }

    function updateCommentCount(postId, count) {
        const btn = document.querySelector(`[data-toggle-comments][data-post-id="${postId}"]`);
        if (!btn) return;
        const span = btn.querySelector('[data-comment-count]');
        if (span) span.textContent = count;
    }

    function submitComment(form) {
        const postId = form.dataset.postId;
        const input = form.querySelector('input[name="contenido"]');
        const contenido = input ? input.value.trim() : '';
        if (!contenido) return;
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        const body = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body,
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then(async (res) => {
                const data = await res.json().catch(() => ({}));
                if (!res.ok) throw new Error(data.message || 'No se pudo publicar el comentario.');
                return data;
            })
            .then((data) => {
                if (!data.success) return;
                appendComment(postId, data.comment);
                updateCommentCount(postId, data.comments_count);
                if (input) input.value = '';
                const section = document.getElementById(`comments-${postId}`);
                if (section) section.style.display = 'block';
            })
            .catch((err) => {
                showToast(err.message || 'Error al enviar el comentario.', 'error');
            })
            .finally(() => {
                if (submitBtn) submitBtn.disabled = false;
            });
    }

    let activeShareMenu = null;

    function closeShareMenu() {
        if (activeShareMenu) {
            activeShareMenu.remove();
            activeShareMenu = null;
        }
    }

    function showRepostForm(postId) {
        closeRepostForm();
        var overlay = document.createElement('div');
        overlay.id = 'repost-overlay';
        overlay.style.cssText = 'position:fixed;inset:0;z-index:10000;background:rgba(10,8,22,0.7);display:flex;align-items:center;justify-content:center;animation:fadeIn 0.15s ease;';
        overlay.addEventListener('click', function(e) { if (e.target === overlay) closeRepostForm(); });

        var box = document.createElement('div');
        box.style.cssText = 'background:var(--bg-panel,#1a1a2e);border:1px solid var(--border-color,rgba(255,255,255,0.08));border-radius:16px;padding:20px;width:90%;max-width:420px;box-shadow:0 20px 60px rgba(0,0,0,0.5);animation:slideUp 0.2s ease;';
        box.innerHTML =
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">' +
            '<h3 style="margin:0;font-size:15px;color:white;display:flex;align-items:center;gap:8px;"><i class="fas fa-retweet" style="color:var(--accent-purple);"></i> Repostear</h3>' +
            '<button onclick="closeRepostForm()" style="background:none;border:none;color:var(--text-muted);font-size:18px;cursor:pointer;"><i class="fas fa-times"></i></button></div>' +
            '<textarea id="repost-comment" placeholder="Añade un comentario (opcional)..." style="width:100%;height:80px;background:var(--bg-dark);color:white;border:1px solid var(--border-color);border-radius:10px;padding:12px;box-sizing:border-box;font-family:inherit;font-size:13px;outline:none;resize:none;margin-bottom:12px;"></textarea>' +
            '<div style="display:flex;justify-content:flex-end;gap:10px;">' +
            '<button onclick="closeRepostForm()" style="padding:8px 16px;border-radius:8px;font-size:12px;font-weight:600;background:none;border:1px solid var(--border-color);color:var(--text-muted);cursor:pointer;">Cancelar</button>' +
            '<button id="repost-submit-btn" style="padding:8px 20px;border-radius:8px;font-size:12px;font-weight:700;border:none;background:var(--accent-purple);color:white;cursor:pointer;box-shadow:0 4px 12px rgba(139,92,246,0.3);"><i class="fas fa-retweet"></i> Repostear</button></div>';

        box.querySelector('#repost-submit-btn').addEventListener('click', function() {
            var text = document.getElementById('repost-comment').value.trim();
            var btn = this;
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>...';
            fetch('/jugador/repost/' + postId, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({ contenido: text || '' }),
            })
            .then(async function(res) {
                var data = await res.json().catch(function() { return {}; });
                if (!res.ok) throw new Error(data.message || 'No se pudo repostear.');
                return data;
            })
            .then(function(data) {
                closeRepostForm();
                showToast('¡Reposteado en tu perfil!', 'success');
                var active = document.querySelector('.feed-tab.active');
                if (active) active.click();
            })
            .catch(function(err) {
                showToast(err.message || 'Error al repostear.', 'error');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-retweet"></i> Repostear';
            });
        });

        overlay.appendChild(box);
        document.body.appendChild(overlay);

        setTimeout(function() {
            document.getElementById('repost-comment').focus();
        }, 100);
    }

    window.closeRepostForm = function() {
        var overlay = document.getElementById('repost-overlay');
        if (overlay) overlay.remove();
    };

    function createShareMenu(btn, postUrl) {
        closeShareMenu();
        const fullUrl = window.location.origin + postUrl;
        const encodedUrl = encodeURIComponent(fullUrl);
        const encodedText = encodeURIComponent('Mira esto en RiftZone!');
        const postId = btn.getAttribute('data-post-id') || '';

        const menu = document.createElement('div');
        menu.className = 'share-menu';
        menu.style.cssText = `
            position: fixed; z-index: 9999; background: var(--bg-panel, #1a1a2e);
            border: 1px solid var(--border-color, rgba(255,255,255,0.08));
            border-radius: 14px; overflow: hidden;
            box-shadow: 0 12px 40px rgba(0,0,0,0.5);
            min-width: 200px; padding: 6px;
            animation: shareMenuIn 0.15s ease;
        `;

        const items = [
            {
                icon: 'fas fa-link',
                label: 'Copiar enlace',
                action: function() {
                    if (navigator.clipboard && navigator.clipboard.writeText) {
                        navigator.clipboard.writeText(fullUrl).then(function() {
                            showToast('Enlace copiado al portapapeles', 'success');
                        });
                    } else {
                        const ta = document.createElement('textarea');
                        ta.value = fullUrl;
                        document.body.appendChild(ta);
                        ta.select();
                        document.execCommand('copy');
                        document.body.removeChild(ta);
                        showToast('Enlace copiado al portapapeles', 'success');
                    }
                }
            },
            {
                icon: 'fab fa-whatsapp',
                label: 'Compartir en WhatsApp',
                action: function() {
                    window.open(`https://wa.me/?text=${encodedText}%20${encodedUrl}`, '_blank');
                }
            },
            {
                icon: 'fab fa-x-twitter',
                label: 'Compartir en X',
                action: function() {
                    window.open(`https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`, '_blank');
                }
            },
        ];

        // Repostear
        items.push({
            icon: 'fas fa-retweet',
            label: 'Repostear',
            action: function() {
                closeShareMenu();
                showRepostForm(postId);
            }
        });

        if (navigator.share) {
            items.push({
                icon: 'fas fa-ellipsis-h',
                label: 'Más...',
                action: function() {
                    navigator.share({ title: 'RiftZone', text: 'Mira esto en RiftZone!', url: fullUrl })
                        .catch(function() {});
                }
            });
        }

        items.forEach(function(item) {
            const row = document.createElement('button');
            row.type = 'button';
            row.style.cssText = `
                display: flex; align-items: center; gap: 12px; width: 100%;
                padding: 10px 14px; border: none; background: none;
                color: var(--text-muted, #a0a0b8); font-size: 13px; font-family: inherit;
                cursor: pointer; border-radius: 10px; transition: all 0.1s;
                text-align: left;
            `;
            row.innerHTML = `<i class="${item.icon}" style="width:18px;text-align:center;font-size:14px;"></i> ${item.label}`;
            row.addEventListener('mouseenter', function() {
                this.style.background = 'rgba(139,92,246,0.1)';
                this.style.color = 'white';
            });
            row.addEventListener('mouseleave', function() {
                this.style.background = 'none';
                this.style.color = 'var(--text-muted, #a0a0b8)';
            });
            row.addEventListener('click', function(e) {
                e.stopPropagation();
                item.action();
                closeShareMenu();
            });
            menu.appendChild(row);
        });

        document.body.appendChild(menu);
        activeShareMenu = menu;

        requestAnimationFrame(function() {
            const rect = btn.getBoundingClientRect();
            const menuRect = menu.getBoundingClientRect();
            let top = rect.bottom + 6;
            let left = rect.left;
            if (top + menuRect.height > window.innerHeight) {
                top = rect.top - menuRect.height - 6;
            }
            if (left + menuRect.width > window.innerWidth) {
                left = window.innerWidth - menuRect.width - 12;
            }
            if (left < 12) left = 12;
            menu.style.top = top + 'px';
            menu.style.left = left + 'px';
        });
    }

    document.addEventListener('click', function(e) {
        const shareBtn = e.target.closest('[data-share-btn]');
        if (shareBtn) {
            e.preventDefault();
            e.stopPropagation();
            const postUrl = shareBtn.getAttribute('data-post-url');
            if (postUrl) {
                createShareMenu(shareBtn, postUrl);
            }
            return;
        }

        if (activeShareMenu) {
            if (!activeShareMenu.contains(e.target)) {
                closeShareMenu();
            }
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeShareMenu();
    });

    document.addEventListener('click', (e) => {
        const likeBtn = e.target.closest('[data-like-btn]');
        if (likeBtn) {
            e.preventDefault();
            toggleLike(likeBtn.dataset.postId, likeBtn);
            return;
        }

        const commentToggle = e.target.closest('[data-toggle-comments]');
        if (commentToggle) {
            e.preventDefault();
            toggleComments(commentToggle.dataset.postId);
        }
    });

    document.addEventListener('submit', (e) => {
        const form = e.target.closest('.comment-form');
        if (!form) return;
        e.preventDefault();
        submitComment(form);
    });

    function getPollResults(parent) {
        const options = parent.querySelectorAll('[data-poll-vote]');
        const results = [];
        options.forEach(function(opt) {
            results.push({
                id: parseInt(opt.dataset.optionId),
                texto: opt.querySelector('.pp-text').textContent,
                votos: parseInt(opt.dataset.votos || 0),
                porcentaje: 0,
            });
        });
        return results;
    }

    function applyPollResults(parent, data) {
        parent.classList.add('post-poll-voted');
        var votedIds = data.voted_options || [];

        parent.querySelectorAll('[data-poll-vote]').forEach(function(opt) {
            var optId = parseInt(opt.dataset.optionId);
            var result = data.results.find(function(r) { return r.id === optId; });
            if (!result) return;
            var bar = opt.querySelector('.pp-bar');
            var pct = opt.querySelector('.pp-pct');
            var votes = opt.querySelector('.pp-votes');
            if (bar) { bar.style.width = result.porcentaje + '%'; bar.style.display = 'block'; }
            if (pct) { pct.textContent = result.porcentaje + '%'; pct.style.display = 'inline'; }
            if (votes) votes.textContent = result.votos + ' votos';
            opt.classList.toggle('pp-opt--voted', votedIds.indexOf(optId) !== -1);
        });
    }

    function sendPollVote(postId, optionId, callback) {
        var formData = new FormData();
        formData.append('option_id', optionId);
        formData.append('csrf_token', getCsrfToken());
        fetch('/jugador/poll/vote/' + postId, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCsrfToken() },
            body: formData,
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) callback(data);
            else showToast(data.message || 'Error al votar.', 'error');
        })
        .catch(function() { showToast('Error de conexión.', 'error'); });
    }

    function openImageLightbox(src) {
        var existing = document.getElementById('image-lightbox');
        if (existing) existing.remove();
        var overlay = document.createElement('div');
        overlay.id = 'image-lightbox';
        overlay.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,0.92);display:flex;align-items:center;justify-content:center;cursor:zoom-out;animation:fadeIn 0.15s ease;';
        overlay.addEventListener('click', function() { overlay.remove(); });
        overlay.addEventListener('keydown', function(e) { if (e.key === 'Escape') overlay.remove(); });
        var img = document.createElement('img');
        img.src = src;
        img.style.cssText = 'max-width:92vw;max-height:92vh;object-fit:contain;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,0.6);';
        overlay.appendChild(img);
        document.body.appendChild(overlay);
        overlay.focus();
        overlay.setAttribute('tabindex', '-1');
    }

    document.addEventListener('click', function(e) {
        var pollBtn = e.target.closest('[data-poll-vote]');
        if (pollBtn) {
            e.preventDefault();
            var postId = pollBtn.dataset.postId || (pollBtn.closest('[data-post-id]') ? pollBtn.closest('[data-post-id]').dataset.postId : null);
            if (!postId) return;
            var optionId = parseInt(pollBtn.dataset.optionId);
            if (!optionId) return;

            var parent = pollBtn.closest('.post-poll');
            if (parent && parent.classList.contains('post-poll-voted')) {
                if (parent.dataset.change !== '1') return;
            }

            sendPollVote(postId, optionId, function(data) {
                if (parent) applyPollResults(parent, data);
            });
            return;
        }

        var postImg = e.target.closest('.post-body > img, .post-detail-content > img, .repost-embed > img, .post-media img, .post-detail-media img');
        if (postImg && !e.target.closest('[data-share-btn]') && !e.target.closest('[data-poll-vote]')) {
            e.stopPropagation();
            openImageLightbox(postImg.src);
            return;
        }
    });

    document.addEventListener('submit', function(e) {
        var pollForm = e.target.closest('.post-poll form');
        if (pollForm) {
            e.preventDefault();
            var postId = pollForm.action.replace(/.*\/poll\/vote\//, '');
            var optionId = pollForm.querySelector('input[name="option_id"]');
            if (!postId || !optionId) return;
            var parent = pollForm.closest('.post-poll');
            if (parent && parent.classList.contains('post-poll-voted')) {
                if (parent.dataset.change !== '1') return;
            }
            sendPollVote(postId, optionId.value, function(data) {
                if (parent) applyPollResults(parent, data);
            });
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var lb = document.getElementById('image-lightbox');
            if (lb) { lb.remove(); }
        }
    });

    document.addEventListener('DOMContentLoaded', () => {
        const hash = window.location.hash;
        if (hash && hash.startsWith('#comments-')) {
            const section = document.querySelector(hash);
            if (section) {
                section.style.display = 'block';
                const input = section.querySelector('.comment-form input[name="contenido"]');
                if (input) input.focus();
            }
        }
    });
})();
