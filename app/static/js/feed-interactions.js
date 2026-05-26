/**
 * Likes y comentarios del feed (dashboard, comunidades).
 */
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
                alert(err.message || 'Error de conexión al dar like.');
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
                alert(err.message || 'Error al enviar el comentario.');
            })
            .finally(() => {
                if (submitBtn) submitBtn.disabled = false;
            });
    }

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
