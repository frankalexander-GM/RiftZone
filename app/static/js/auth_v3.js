/* ═══════════════════════════════════════════════
   RiftZone Auth v3 — Shared JavaScript
   Stars, Particles, Confetti, Toast, UX
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function() {

    // ═══ STARS ═══
    (function() {
        var c = document.getElementById('stars-canvas');
        if (!c) return;
        var ctx = c.getContext('2d');
        var stars = [];
        function resize() { c.width = window.innerWidth; c.height = window.innerHeight; }
        window.addEventListener('resize', resize); resize();
        for (var i = 0; i < 200; i++) {
            stars.push({ x: Math.random()*c.width, y: Math.random()*c.height, r: Math.random()*1.2+0.3, a: Math.random(), speed: Math.random()*0.003+0.001, phase: Math.random()*Math.PI*2 });
        }
        function draw(t) {
            ctx.clearRect(0,0,c.width,c.height);
            for (var i=0;i<stars.length;i++) {
                var s=stars[i], alpha=0.3+0.7*Math.abs(Math.sin(t*s.speed+s.phase));
                ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
                ctx.fillStyle='rgba(255,255,255,'+(alpha*0.6)+')'; ctx.fill();
            }
            requestAnimationFrame(draw);
        }
        requestAnimationFrame(draw);
    })();

    // ═══ FLOATING PARTICLES ═══
    (function() {
        var c = document.getElementById('particles');
        if (!c) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        var ctx = c.getContext('2d'), pts = [], mouse = {x:-9999,y:-9999}, w, h;
        function resize() { w=c.width=window.innerWidth; h=c.height=window.innerHeight; }
        window.addEventListener('resize', resize); resize();
        document.addEventListener('mousemove', function(e) { mouse.x=e.clientX; mouse.y=e.clientY; });
        var colors = ['139,92,246','236,72,153','6,182,212','250,204,21'];
        for (var i=0;i<80;i++) {
            pts.push({ x:Math.random()*w, y:Math.random()*h, vx:(Math.random()-0.5)*0.4, vy:(Math.random()-0.5)*0.4, r:Math.random()*2+0.8, color:colors[Math.floor(Math.random()*colors.length)], alpha:Math.random()*0.5+0.1, base:Math.random()*0.5+0.1 });
        }
        function frame() {
            ctx.clearRect(0,0,w,h);
            for (var i=0;i<pts.length;i++) { for (var j=i+1;j<pts.length;j++) { var dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y, d=Math.sqrt(dx*dx+dy*dy); if(d<100){ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);ctx.strokeStyle='rgba(139,92,246,'+((1-d/100)*0.06)+')';ctx.lineWidth=0.5;ctx.stroke();}} }
            for (var i=0;i<pts.length;i++) {
                var p=pts[i], mdx=p.x-mouse.x, mdy=p.y-mouse.y, md=Math.sqrt(mdx*mdx+mdy*mdy);
                if(md<130){var f=(130-md)/130;p.vx+=(mdx/md)*f*0.2;p.vy+=(mdy/md)*f*0.2;p.alpha=Math.min(p.base+f*0.6,1);}else{p.alpha+=(p.base-p.alpha)*0.03;}
                p.vx*=0.99;p.vy*=0.99;p.x+=p.vx;p.y+=p.vy;
                if(p.x<-20)p.x=w+20;if(p.x>w+20)p.x=-20;if(p.y<-20)p.y=h+20;if(p.y>h+20)p.y=-20;
                ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle='rgba('+p.color+','+p.alpha+')';ctx.fill();
                ctx.beginPath();ctx.arc(p.x,p.y,p.r*4,0,Math.PI*2);ctx.fillStyle='rgba('+p.color+','+(p.alpha*0.03)+')';ctx.fill();
            }
            requestAnimationFrame(frame);
        }
        frame();
    })();

    // ═══ CONFETTI ═══
    window.launchConfetti = function() {
        var cv = document.getElementById('confetti');
        if (!cv) return;
        var ctx = cv.getContext('2d');
        function resize() { cv.width=window.innerWidth; cv.height=window.innerHeight; }
        window.addEventListener('resize', resize); resize();
        var pieces = [], colors = ['#8B5CF6','#EC4899','#06B6D4','#F59E0B','#10B981','#F43F5E','#A78BFA'];
        for (var i=0;i<120;i++) {
            pieces.push({ x:cv.width/2+(Math.random()-0.5)*200, y:cv.height/2-100, vx:(Math.random()-0.5)*16, vy:Math.random()*-18-4, w:Math.random()*8+4, h:Math.random()*4+2, color:colors[Math.floor(Math.random()*colors.length)], rot:Math.random()*360, rotV:(Math.random()-0.5)*12, gravity:0.25+Math.random()*0.15, drag:0.98+Math.random()*0.015, alpha:1 });
        }
        function animate() {
            ctx.clearRect(0,0,cv.width,cv.height);
            for (var i=pieces.length-1;i>=0;i--) {
                var p=pieces[i]; p.vx*=p.drag; p.vy+=p.gravity; p.vy*=p.drag; p.x+=p.vx; p.y+=p.vy; p.rot+=p.rotV;
                if(p.y>cv.height+20) p.alpha-=0.02;
                if(p.alpha<=0){pieces.splice(i,1);continue;}
                ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.rot*Math.PI/180); ctx.globalAlpha=Math.max(0,p.alpha);
                ctx.fillStyle=p.color; ctx.fillRect(-p.w/2,-p.h/2,p.w,p.h); ctx.restore();
            }
            if(pieces.length>0) requestAnimationFrame(animate);
            else ctx.clearRect(0,0,cv.width,cv.height);
        }
        animate();
    };

    // ═══ TOAST ═══
    window.showToast = function(msg, type) {
        type = type || 'success';
        var box = document.getElementById('toasts');
        if (!box) { box = document.createElement('div'); box.id='toasts'; document.body.appendChild(box); }
        var cls = (type==='error'||type==='err') ? 'err' : 'ok';
        var icon = cls==='err' ? 'fa-circle-exclamation' : 'fa-circle-check';
        var t = document.createElement('div');
        t.className = 'toast toast--' + cls;
        t.innerHTML = '<i class="fas '+icon+'"></i><span>'+msg+'</span><div class="progress"></div>';
        box.appendChild(t);
        setTimeout(function(){ t.classList.add('out'); setTimeout(function(){ t.remove(); }, 400); }, 3500);
    };

    // ═══ FLASH MESSAGES ═══
    (function() {
        var el = document.getElementById('flash-data');
        if (!el) return;
        try {
            var messages = JSON.parse(el.getAttribute('data-messages') || '[]');
            if (Array.isArray(messages)) {
                messages.forEach(function(item) {
                    if (Array.isArray(item)) { showToast(item[1], item[0]==='error' ? 'error' : 'success'); }
                });
            }
        } catch(e) {}
        el.remove();
    })();

    // ═══ PASSWORD TOGGLE (global) ═══
    window.togglePassword = function(id, btn) {
        var input = document.getElementById(id);
        if (!input) return;
        var isHidden = input.type === 'password';
        input.type = isHidden ? 'text' : 'password';
        btn.innerHTML = isHidden ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
        btn.setAttribute('aria-label', isHidden ? 'Ocultar contraseña' : 'Mostrar contraseña');
        input.focus();
    };

    // ═══ TYPING INDICATOR ═══
    var typingTimers = {};
    document.querySelectorAll('.field input').forEach(function(input) {
        var field = input.closest('.field');
        if (!field) return;
        input.addEventListener('input', function() {
            field.classList.add('typing');
            clearTimeout(typingTimers[field.id || '']);
            typingTimers[field.id || ''] = setTimeout(function() { field.classList.remove('typing'); }, 600);
        });
    });

    // ═══ REAL-TIME VALIDATION ═══
    document.querySelectorAll('.field input[required]').forEach(function(input) {
        var field = input.closest('.field');
        if (!field) return;
        input.addEventListener('input', function() {
            field.classList.remove('error');
            var val = this.value.trim();
            if (val.length > 0) field.classList.add('valid');
            else field.classList.remove('valid');
        });
    });

    // ═══ CAPS LOCK ═══
    document.querySelectorAll('.caps-warning').forEach(function(warn) {
        var input = warn.closest('.input-box').querySelector('input');
        if (!input) return;
        input.addEventListener('keyup', function(e) {
            var capsOn = e.getModifierState && e.getModifierState('CapsLock');
            warn.classList.toggle('show', capsOn && this.value.length > 0);
        });
        input.addEventListener('blur', function() { warn.classList.remove('show'); });
    });

    // ═══ PASSWORD STRENGTH ═══
    window.updatePasswordStrength = function(pw) {
        var container = document.getElementById('pwd-strength');
        if (!container) return;
        var text = document.getElementById('strength-text');
        var segs = [document.getElementById('seg1'),document.getElementById('seg2'),document.getElementById('seg3'),document.getElementById('seg4')];
        var reqLen = document.getElementById('req-len');
        var reqNum = document.getElementById('req-num');
        var reqUpper = document.getElementById('req-upper');
        if (!pw.length) { container.classList.remove('show'); return; }
        container.classList.add('show');
        var score=0, hasLen=pw.length>=6, hasNum=/\d/.test(pw), hasUpper=/[A-Z]/.test(pw), hasSpecial=/[^A-Za-z0-9]/.test(pw);
        if(hasLen) score++; if(hasNum) score++; if(hasUpper) score++; if(hasSpecial) score++;
        if(reqLen){ reqLen.classList.toggle('met',hasLen); reqLen.querySelector('i').className=hasLen?'fas fa-check':'fas fa-circle'; }
        if(reqNum){ reqNum.classList.toggle('met',hasNum); reqNum.querySelector('i').className=hasNum?'fas fa-check':'fas fa-circle'; }
        if(reqUpper){ reqUpper.classList.toggle('met',hasUpper); reqUpper.querySelector('i').className=hasUpper?'fas fa-check':'fas fa-circle'; }
        var labels=['','Débil','Regular','Buena','Fuerte'];
        var classes=['','weak','fair','good','strong'];
        var activeCount=Math.max(1,score);
        for(var i=0;i<4;i++) segs[i].classList.toggle('active',i<activeCount);
        text.textContent=labels[activeCount]; text.className='text '+classes[activeCount];
    };

    // ═══ RIPPLE ═══
    document.querySelectorAll('.btn-submit, .btn-guest').forEach(function(btn) {
        btn.addEventListener('mousedown', function(e) {
            var rect=this.getBoundingClientRect(), ripple=document.createElement('span');
            ripple.className='ripple'; var size=Math.max(rect.width,rect.height);
            ripple.style.width=ripple.style.height=size+'px';
            ripple.style.left=(e.clientX-rect.left-size/2)+'px';
            ripple.style.top=(e.clientY-rect.top-size/2)+'px';
            this.appendChild(ripple); setTimeout(function(){ripple.remove();},600);
        });
    });

    // ═══ CARD 3D TILT ═══
    (function() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        var card = document.querySelector('.card');
        if (!card) return;
        card.addEventListener('mousemove', function(e) {
            var rect=card.getBoundingClientRect(), x=(e.clientX-rect.left)/rect.width-0.5, y=(e.clientY-rect.top)/rect.height-0.5;
            var inner=document.getElementById('card-inner');
            if(inner && !inner.classList.contains('success-state')) inner.style.transform='rotateY('+x*2+'deg) rotateX('+(-y*2)+'deg)';
        });
        card.addEventListener('mouseleave', function() {
            var inner=document.getElementById('card-inner');
            if(inner && !inner.classList.contains('success-state')) inner.style.transform='';
        });
    })();

    // ═══ KEYBOARD HINT VISIBILITY ═══
    var kbHint = document.getElementById('keyboard-hint');
    if (kbHint) {
        document.querySelectorAll('form input[type="text"], form input[type="password"], form input[type="email"]').forEach(function(inp) {
            inp.addEventListener('focus', function() { kbHint.style.opacity='1'; });
            inp.addEventListener('blur', function() { kbHint.style.opacity='0'; });
        });
    }
});