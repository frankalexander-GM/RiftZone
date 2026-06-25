(function(){
   var activeTab = document.querySelector('.feed-tab.active');
   var indicator = document.getElementById('tab-indicator');

   function moveIndicator(tab) {
     if (!indicator || !tab) return;
     var parent = tab.closest('.feed-tabs');
     if (!parent) return;
     var parentRect = parent.getBoundingClientRect();
     var tabRect = tab.getBoundingClientRect();
     indicator.style.left = (tabRect.left - parentRect.left + parent.scrollLeft) + 'px';
     indicator.style.width = tabRect.width + 'px';
   }

   if (activeTab) {
     moveIndicator(activeTab);
   }

   window.addEventListener('resize', function() {
     var a = document.querySelector('.feed-tab.active');
     if (a) moveIndicator(a);
   });

   function renderPosts(posts) {
     var feed = document.querySelector('.main-feed');
     if (!feed) return;
     var postItems = feed.querySelectorAll('.post-item, .empty-feed');
     postItems.forEach(function(el) { el.remove(); });
     if (!posts || posts.length === 0) {
       var empty = document.createElement('div');
       empty.className = 'empty-feed';
       empty.innerHTML = '<i class="far fa-newspaper"></i><h3>Aún no hay publicaciones</h3><p>Sé el primero en compartir algo con la comunidad.</p>';
       feed.appendChild(empty);
       return;
     }
      posts.forEach(function(p) {
        var el = document.createElement('div');
        el.className = 'post-item';
        var avatar = p.autor.foto_perfil || '/static/img/default-avatar.png';
        var postBody = '';
        // Repost embed
        if (p.repost_id && p.reposteado) {
          var origUrl = '/jugador/perfil/' + p.reposteado.autor.username;
          postBody += '<p>' + (p.contenido !== '[Repost]' ? escapeHtml(p.contenido) : '') + '</p>';
          postBody += '<div class="repost-embed"><a href="' + origUrl + '" class="repost-header" onclick="event.stopPropagation();">' +
            '<img src="' + (p.reposteado.autor.foto_perfil || '/static/img/default-avatar.png') + '" alt="">' +
            '<span class="repost-name">' + escapeHtml(p.reposteado.autor.nombre) + '</span></a>' +
            '<div class="repost-content">' + escapeHtml(p.reposteado.contenido) + '</div>';
          if (p.reposteado.imagen_url) {
            postBody += '<img src="' + p.reposteado.imagen_url + '" alt="" style="width:100%;border-radius:8px;margin-top:6px;max-height:200px;object-fit:cover;">';
          }
          if (p.reposteado.is_poll && p.reposteado.poll) {
            postBody += '<div class="post-poll" style="margin-top:8px;" data-post-id="' + p.reposteado.id_publicacion + '" data-change="0"><div class="pp-q">' + escapeHtml(p.reposteado.poll.pregunta) + '</div>';
            p.reposteado.poll.options.forEach(function(opt) {
              postBody += '<button type="button" class="pp-opt" data-poll-vote data-option-id="' + opt.id + '" data-votos="' + opt.votos + '">' +
                '<span class="pp-text">' + escapeHtml(opt.texto) + '</span>' +
                '<span class="pp-votes">' + opt.votos + ' votos</span>' +
                '<span class="pp-bar" style="display:none;"></span>' +
                '<span class="pp-pct" style="display:none;"></span></button>';
            });
            postBody += '</div>';
          }
          postBody += '</div>';
        } else {
          postBody += '<p>' + escapeHtml(p.contenido) + '</p>';
          if (p.video_archivo) {
            postBody += '<video src="' + p.video_archivo + '" controls style="width:100%;border-radius:12px;max-height:400px;background:#000;" preload="metadata"></video>';
          } else if (p.imagen_url && (p.imagen_url.endsWith('.mp4') || p.imagen_url.endsWith('.mov') || p.imagen_url.endsWith('.avi'))) {
            postBody += '<video src="' + p.imagen_url + '" controls style="width:100%;border-radius:12px;max-height:400px;background:#000;" preload="metadata"></video>';
          } else if (p.imagen_url) {
            postBody += '<img src="' + p.imagen_url + '" alt="" loading="lazy">';
          }
          if (p.is_poll && p.poll) {
            postBody += '<div class="post-poll" data-post-id="' + p.id_publicacion + '" data-change="0"><div class="pp-q">' + escapeHtml(p.poll.pregunta) + '</div>';
            p.poll.options.forEach(function(opt) {
              postBody += '<button type="button" class="pp-opt" data-poll-vote data-option-id="' + opt.id + '" data-votos="' + opt.votos + '">' +
                '<span class="pp-text">' + escapeHtml(opt.texto) + '</span>' +
                '<span class="pp-votes">' + opt.votos + ' votos</span>' +
                '<span class="pp-bar" style="display:none;"></span>' +
                '<span class="pp-pct" style="display:none;"></span></button>';
            });
            postBody += '</div>';
          }
        }
       var viewPostUrl = '/jugador/publicacion/' + p.id_publicacion;
       el.innerHTML =
         '<div class="post-head">' +
           '<a href="/jugador/perfil/' + p.autor.username + '"><img src="' + avatar + '" alt="" class="ph-avatar"></a>' +
           '<a href="/jugador/perfil/' + p.autor.username + '" class="ph-info">' +
               '<div class="ph-name">' + escapeHtml(p.autor.nombre) + '</div>' +
               '<div class="ph-meta"><span>@' + p.autor.username + '</span>' +
               (p.juego ? '<a href="/jugador/comunidad/' + encodeURIComponent(p.juego) + '" class="ph-game-tag" onclick="event.stopPropagation();">' + escapeHtml(p.juego) + '</a>' : '<span class="ph-game-tag ph-game-tag--general">General</span>') +
               '<span>' + timeAgo(p.fecha_creacion) + '</span></div></a>' +
           '<div class="ph-badges">' +
             (p.is_poll ? '<span class="badge badge-blue" style="font-size:10px;"><i class="fas fa-poll"></i></span>' : '') +
             (p.promocionada || p.boost_tipo ? '<span class="badge badge-yellow" style="font-size:10px;"><i class="fas fa-rocket"></i></span>' : '') +
           '</div></div>' +
         '<div class="post-body">' + postBody + '</div>' +
         '<div class="post-foot">' +
           '<button data-like-btn data-post-id="' + p.id_publicacion + '" class="pf-btn' + (p.liked ? ' liked' : '') + '"><i class="' + (p.liked ? 'fas' : 'far') + ' fa-heart"></i> <span id="like-count-' + p.id_publicacion + '">' + p.likes_count + '</span></button>' +
           '<button data-toggle-comments data-post-id="' + p.id_publicacion + '" class="pf-btn"><i class="far fa-comment"></i> <span data-comment-count>' + p.comentarios_count + '</span></button>' +
           '<button data-share-btn data-post-id="' + p.id_publicacion + '" data-post-url="' + viewPostUrl + '" class="pf-btn" title="Compartir"><i class="fas fa-share-alt"></i></button>' +
           '<div class="pf-right">' +
              (p.juego ? '<a href="/jugador/comunidad/' + encodeURIComponent(p.juego) + '" class="pf-btn"><i class="fas fa-tag"></i></a>' : '') +
              (p.imagen_url || p.video_archivo ? '<a href="' + viewPostUrl + '" class="pf-btn" title="Ver publicación"><i class="fas fa-external-link-alt"></i></a>' : '') +
             '<a href="/jugador/boosts" class="pf-btn" title="Boost"><i class="fas fa-rocket"></i></a></div></div>' +
         '<div id="comments-' + p.id_publicacion + '" class="comments-section" style="display:none;">' +
           '<div id="comments-list-' + p.id_publicacion + '"></div>' +
           '<form class="comment-form" data-post-id="' + p.id_publicacion + '" action="/jugador/comentar/' + p.id_publicacion + '" method="POST">' +
             '<input type="hidden" name="csrf_token" value="' + getCSRFToken() + '"/>' +
             '<input type="text" name="contenido" placeholder="Escribe un comentario..." required>' +
             '<button type="submit"><i class="fas fa-paper-plane"></i></button></form></div>';
       feed.appendChild(el);
     });
   }

   function escapeHtml(text) {
     if (!text) return '';
     var d = document.createElement('div');
     d.textContent = text;
     return d.innerHTML;
   }

   function timeAgo(iso) {
     if (!iso) return '';
     var now = new Date();
     var d = new Date(iso);
     var diff = Math.floor((now - d) / 1000);
     if (diff < 60) return 'hace un momento';
     if (diff < 3600) return 'hace ' + Math.floor(diff / 60) + 'm';
     if (diff < 86400) return 'hace ' + Math.floor(diff / 3600) + 'h';
     return 'hace ' + Math.floor(diff / 86400) + 'd';
   }

   function getCSRFToken() {
     var meta = document.querySelector('meta[name="csrf-token"]');
     return meta ? meta.getAttribute('content') : '';
   }

   var tabs = document.querySelectorAll('.feed-tab');
   tabs.forEach(function(t){
     t.addEventListener('click', function(){
       tabs.forEach(function(x){ x.classList.remove('active'); x.removeAttribute('aria-selected'); });
       this.classList.add('active');
       this.setAttribute('aria-selected', 'true');
       moveIndicator(this);
       var tab = this.getAttribute('data-tab');
        fetch('/jugador/api/feed?tab=' + tab, {
         headers: { 'X-Requested-With': 'XMLHttpRequest' }
       })
       .then(function(r) { return r.json(); })
       .then(function(data) {
         if (data.posts) renderPosts(data.posts);
       })
       .catch(function(err) { console.error('Error loading feed:', err); });
     });
   });

   document.querySelectorAll('.create-post-card').forEach(function(card){
     card.querySelectorAll('.cp-actions button').forEach(function(b){
       b.addEventListener('click', function(e){ e.stopPropagation(); });
     });
   });
   window.switchModalType = function(type) {
       // Update pills
       document.querySelectorAll('.modal-type-pill').forEach(function(p) {
         p.classList.toggle('active', p.getAttribute('data-type') === type);
       });
       // Hide all forms
       document.querySelectorAll('.post-creation-form').forEach(function(f) {
         f.style.display = 'none';
       });
       // Show requested form
       var activeForm = document.getElementById('post-form-' + type);
       if (activeForm) {
         activeForm.style.display = 'block';
       }
       
       // Update title
       var title = 'Crear publicación';
       if (type === 'texto') title = 'Crear publicación';
       else if (type === 'imagen') title = 'Compartir Imagen';
       else if (type === 'video') title = 'Subir Video';
       else if (type === 'clip') title = 'Subir Clip (máx 1 minuto)';
       else if (type === 'encuesta') title = 'Crear Encuesta';
       
       var modalTitle = document.getElementById('modal-title');
       if (modalTitle) {
         modalTitle.innerHTML = '<i class="fas fa-edit" style="color:var(--accent-purple);"></i> ' + title;
       }
     };

     window.openPostModal = function(type) {
       var modal = document.getElementById('post-modal');
       if (!modal) return;
       switchModalType(type);
       modal.style.display = 'flex';
     };

    window.closePostModal = function() {
      var modal = document.getElementById('post-modal');
      if (!modal) return;
      modal.style.display = 'none';
      
      document.querySelectorAll('.post-creation-form').forEach(function(f) {
        f.reset();
      });
      removeImagePreview();
      removeVideoPreview();
      removeClipPreview();
    };

    window.addPollOption = function() {
      var container = document.getElementById('poll-options-container');
      if (!container) return;
      var count = container.querySelectorAll('input').length + 1;
      var input = document.createElement('input');
      input.type = 'text';
      input.name = 'poll_op[]';
      input.placeholder = 'Opción ' + count;
      input.style.width = '100%';
      input.style.background = 'var(--bg-dark)';
      input.style.color = 'white';
      input.style.border = '1px solid var(--border-color)';
      input.style.borderRadius = '10px';
      input.style.padding = '10px 12px';
      input.style.outline = 'none';
      input.style.fontFamily = 'inherit';
      input.style.fontSize = '13px';
      container.appendChild(input);
    };

    window.previewImage = function(input) {
      if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
          document.getElementById('image-preview').src = e.target.result;
          document.getElementById('image-preview-container').style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
      }
    };

    window.removeImagePreview = function() {
      var img = document.getElementById('image-preview');
      if (img) img.src = '#';
      var container = document.getElementById('image-preview-container');
      if (container) container.style.display = 'none';
      var fileInput = document.getElementById('img-file-input');
      if (fileInput) fileInput.value = '';
    };

    window.previewVideo = function(input) {
      if (input.files && input.files[0]) {
        var file = input.files[0];
        var url = URL.createObjectURL(file);
        document.getElementById('video-preview-tag').src = url;
        document.getElementById('video-filename-label').innerText = file.name;
        document.getElementById('video-preview-container').style.display = 'block';
      }
    };

     window.removeVideoPreview = function() {
       var video = document.getElementById('video-preview-tag');
       if (video && video.src) URL.revokeObjectURL(video.src);
       if (video) video.src = '';
       var label = document.getElementById('video-filename-label');
       if (label) label.innerText = '';
       var container = document.getElementById('video-preview-container');
       if (container) container.style.display = 'none';
       var fileInput = document.getElementById('video-file-input');
       if (fileInput) fileInput.value = '';
     };

     window.previewClip = function(input) {
       if (!input.files || !input.files[0]) return;
       var file = input.files[0];
       var url = URL.createObjectURL(file);
       var tempVideo = document.createElement('video');
       tempVideo.preload = 'metadata';
       tempVideo.onloadedmetadata = function() {
         var dur = tempVideo.duration;
         if (dur > 60) {
           alert('El clip no puede durar más de 1 minuto (' + Math.round(dur) + 's).');
           input.value = '';
           URL.revokeObjectURL(url);
           return;
         }
         document.getElementById('clip-preview-tag').src = url;
         document.getElementById('clip-filename-label').innerText = file.name;
         document.getElementById('clip-duration-label').innerText = Math.round(dur) + 's';
         document.getElementById('clip-preview-container').style.display = 'block';
       };
       tempVideo.onerror = function() {
         URL.revokeObjectURL(url);
       };
       tempVideo.src = url;
     };

     window.removeClipPreview = function() {
       var video = document.getElementById('clip-preview-tag');
       if (video && video.src) URL.revokeObjectURL(video.src);
       if (video) video.src = '';
       var label = document.getElementById('clip-filename-label');
       if (label) label.innerText = '';
       var durLabel = document.getElementById('clip-duration-label');
       if (durLabel) durLabel.innerText = '';
       var container = document.getElementById('clip-preview-container');
       if (container) container.style.display = 'none';
       var fileInput = document.getElementById('clip-file-input');
       if (fileInput) fileInput.value = '';
     };

    (function() {
      document.querySelectorAll('.post-creation-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
          e.preventDefault();
          var formData = new FormData(form);
          var csrfToken = form.querySelector('input[name="csrf_token"]').value;
          
          var submitBtn = form.querySelector('button[type="submit"]');
          submitBtn.disabled = true;
          submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publicando...';
          
          fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': csrfToken
            }
          })
          .then(function(response) { return response.json(); })
          .then(function(data) {
             if (data.success) {
               var post = data.post;
               var authorAvatar = post.autor.foto_perfil ? post.autor.foto_perfil : '/static/img/default-avatar.png';
               var viewPostUrl = '/jugador/publicacion/' + post.id_publicacion;
               
               var postBody = '';
               postBody += '<p>' + escapeHtml(post.contenido) + '</p>';
               if (post.imagen_url) {
                 if (post.imagen_url.endsWith('.mp4') || post.imagen_url.endsWith('.mov') || post.imagen_url.endsWith('.avi')) {
                   postBody += '<video src="' + post.imagen_url + '" controls style="width:100%;border-radius:12px;max-height:400px;background:#000;" preload="metadata"></video>';
                 } else {
                   postBody += '<img src="' + post.imagen_url + '" alt="" loading="lazy">';
                 }
               }
               if (post.video_archivo) {
                 postBody += '<video src="' + post.video_archivo + '" controls style="width:100%;border-radius:12px;max-height:400px;background:#000;" preload="metadata"></video>';
               }
               if (post.is_poll && post.poll) {
                 postBody += '<div class="post-poll" data-post-id="' + post.id_publicacion + '" data-change="' + (post.poll.allow_change ? '1' : '0') + '">';
                 postBody += '<div class="pp-q">' + escapeHtml(post.poll.pregunta) + '</div>';
                 post.poll.options.forEach(function(opt) {
                   postBody += '<button type="button" class="pp-opt" data-poll-vote data-option-id="' + opt.id + '" data-votos="' + opt.votos + '">';
                   postBody += '<span class="pp-text">' + escapeHtml(opt.texto) + '</span>' +
                              '<span class="pp-votes">' + opt.votos + ' votos</span>' +
                              '<span class="pp-bar" style="display:none;"></span>' +
                              '<span class="pp-pct" style="display:none;"></span>';
                   postBody += '</button>';
                 });
                 postBody += '</div>';
               }
               
               var postElement = document.createElement('div');
               postElement.className = 'post-item';
               postElement.innerHTML = 
                 '<div class="post-head">' +
                   '<a href="/jugador/perfil/' + post.autor.username + '"><img src="' + authorAvatar + '" alt="" class="ph-avatar"></a>' +
                     '<a href="/jugador/perfil/' + post.autor.username + '" class="ph-info">' +
                       '<div class="ph-name">' + escapeHtml(post.autor.nombre) + '</div>' +
                       '<div class="ph-meta">' +
                         '<span>@' + post.autor.username + '</span>' +
                         (post.juego ? '<a href="/jugador/comunidad/' + encodeURIComponent(post.juego) + '" class="ph-game-tag" onclick="event.stopPropagation();">' + escapeHtml(post.juego) + '</a>' : '<span class="ph-game-tag ph-game-tag--general">General</span>') +
                         '<span>hace un momento</span>' +
                       '</div>' +
                     '</a>' +
                   '<div class="ph-badges"></div>' +
                 '</div>' +
                 '<div class="post-body">' + postBody + '</div>' +
                 '<div class="post-foot">' +
                   '<button data-like-btn data-post-id="' + post.id_publicacion + '" class="pf-btn"><i class="far fa-heart"></i> <span id="like-count-' + post.id_publicacion + '">0</span></button>' +
                   '<button data-toggle-comments data-post-id="' + post.id_publicacion + '" class="pf-btn"><i class="far fa-comment"></i> <span data-comment-count>0</span></button>' +
                    '<button data-share-btn data-post-id="' + post.id_publicacion + '" data-post-url="' + viewPostUrl + '" class="pf-btn" title="Compartir"><i class="fas fa-share-alt"></i></button>' +
                   '<div class="pf-right">' +
                      (post.juego ? '<a href="/jugador/comunidad/' + encodeURIComponent(post.juego) + '" class="pf-btn"><i class="fas fa-tag"></i></a>' : '') +
                      (post.imagen_url || post.video_archivo ? '<a href="' + viewPostUrl + '" class="pf-btn" title="Ver publicación"><i class="fas fa-external-link-alt"></i></a>' : '') +
                      '<a href="/jugador/boosts" class="pf-btn" title="Boost"><i class="fas fa-rocket"></i></a>' +
                   '</div>' +
                 '</div>' +
                 '<div id="comments-' + post.id_publicacion + '" class="comments-section" style="display:none;">' +
                   '<div id="comments-list-' + post.id_publicacion + '"></div>' +
                   '<form class="comment-form" data-post-id="' + post.id_publicacion + '" action="/jugador/comentar/' + post.id_publicacion + '" method="POST">' +
                     '<input type="hidden" name="csrf_token" value="' + getCSRFToken() + '"/>' +
                     '<input type="text" name="contenido" placeholder="Escribe un comentario..." required>' +
                     '<button type="submit"><i class="fas fa-paper-plane"></i></button>' +
                   '</form>' +
                 '</div>';
               
               var feed = document.querySelector('.main-feed');
               if (feed) {
                 var firstChild = feed.firstChild;
                 if (firstChild) {
                   feed.insertBefore(postElement, firstChild);
                 } else {
                   feed.appendChild(postElement);
                 }
                 var empty = feed.querySelector('.empty-feed');
                 if (empty) empty.remove();
               }
               closePostModal();
            } else {
              console.error('Error:', data.message);
              alert(data.message || 'Hubo un error. Intenta de nuevo.');
            }
          })
          .catch(function(err) { console.error(err); alert('Error de conexión.'); })
          .finally(function() {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Publicar';
          });
        });
      });
    })();

})();
