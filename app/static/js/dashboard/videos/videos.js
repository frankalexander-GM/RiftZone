(function() {
  // Filter tabs
  var tabs = document.querySelectorAll('.vf-tab');
  tabs.forEach(function(tab) {
    tab.addEventListener('click', function() {
      tabs.forEach(function(t) { t.classList.remove('active'); });
      this.classList.add('active');
      var filter = this.getAttribute('data-filter');
      var cards = document.querySelectorAll('.video-card');
      cards.forEach(function(card) { card.style.display = 'block'; });
    });
  });

  // Pause other videos when playing one
  document.querySelectorAll('.vc-player video').forEach(function(video) {
    video.addEventListener('play', function() {
      document.querySelectorAll('.vc-player video').forEach(function(other) {
        if (other !== video) other.pause();
      });
    });
  });
})();