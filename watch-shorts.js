(() => {
  'use strict';
  const section = document.querySelector('[data-watch-shorts]');
  if (!section) return;
  let active = null;
  let apiPromise;
  function loadAPI() {
    if (window.YT && window.YT.Player) return Promise.resolve(window.YT);
    if (apiPromise) return apiPromise;
    apiPromise = new Promise((resolve, reject) => {
      const prior = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = () => {
        if (typeof prior === 'function') prior();
        resolve(window.YT);
      };
      const script = document.createElement('script');
      script.src = 'https://www.youtube.com/iframe_api';
      script.onerror = () => reject(new Error('Player unavailable'));
      document.head.append(script);
    });
    return apiPromise;
  }
  function stop(returnFocus) {
    if (!active) return;
    const previous = active;
    active = null;
    clearTimeout(previous.timer);
    if (previous.player) previous.player.destroy();
    previous.mount.remove();
    previous.button.remove();
    previous.status.remove();
    previous.preview.hidden = false;
    if (returnFocus) previous.link.focus();
  }
  function unavailable(state) {
    if (active !== state) return;
    const copy = state.card.querySelector('.watch-short-copy');
    const status = state.status;
    stop(false);
    status.textContent = 'You can watch this Short on YouTube using the link below.';
    copy.insertBefore(status, copy.querySelector('a'));
    state.link.focus();
  }
  section.addEventListener('click', event => {
    const link = event.target.closest('[data-short-play]');
    if (!link || !section.contains(link) || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const id = link.dataset.shortPlay;
    if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return;
    event.preventDefault();
    stop(false);
    section.querySelectorAll('.watch-short-status').forEach(node => node.remove());
    const card = link.closest('.watch-short');
    const preview = card.querySelector('.watch-short-preview');
    const mount = document.createElement('div');
    mount.className = 'watch-short-player';
    const placeholder = document.createElement('div');
    mount.append(placeholder);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'watch-short-stop';
    button.textContent = 'Close video';
    button.addEventListener('click', () => stop(true));
    const status = document.createElement('p');
    status.className = 'watch-short-status';
    status.setAttribute('role', 'status');
    status.textContent = 'Opening the video…';
    preview.parentElement.append(mount);
    card.querySelector('.watch-short-copy').append(status, button);
    const state = { link, preview, card, mount, button, status, player: null, timer: null };
    active = state;
    state.timer = setTimeout(() => unavailable(state), 15000);
    button.focus();
    loadAPI().then(YT => {
      if (active !== state) return;
      state.player = new YT.Player(placeholder, {
        width: '100%', height: '100%', videoId: id,
        playerVars: { autoplay: 0, playsinline: 1, rel: 0, origin: window.location.origin },
        events: {
          onReady: event => {
            if (active !== state) { event.target.destroy(); return; }
            clearTimeout(state.timer);
            preview.hidden = true;
            mount.dataset.ready = 'true';
            status.textContent = '';
            event.target.getIframe().title = 'YouTube video: ' + card.querySelector('h3').textContent;
            // Only this visitor's explicit click requests playback.
            event.target.playVideo();
          },
          onError: () => unavailable(state)
        }
      });
    }).catch(() => unavailable(state));
  });
  section.addEventListener('keydown', event => {
    if (event.key === 'Escape' && active) { event.preventDefault(); stop(true); }
  });
  window.addEventListener('pagehide', () => stop(false));
})();
