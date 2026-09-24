(() => {
  'use strict';
  const section = document.querySelector('[data-watch-shorts]');
  if (!section) return;
  let active = null;
  let apiPromise;
  const more = section.querySelector('[data-shorts-more]');
  const summary = more && more.querySelector('summary');
  const desktop = window.matchMedia('(min-width: 1024px)');
  let mobileOpen = more ? more.open : false;
  function syncViewport() {
    if (!more) return;
    const hiddenControlFocused = document.activeElement === summary || document.activeElement === more.querySelector('[data-shorts-collapse]');
    section.toggleAttribute('data-shorts-desktop', desktop.matches);
    more.open = desktop.matches || mobileOpen;
    syncDisclosure();
    if (desktop.matches && hiddenControlFocused) more.querySelector('[data-short-play]').focus({ preventScroll: true });
  }
  function syncDisclosure() {
    if (!more) return;
    more.querySelector('[data-shorts-toggle-label]').textContent = more.open ? 'Hide 3 Shorts' : 'Show 3 more Shorts';
    if (!more.open) {
      const focusInside = more.contains(document.activeElement) && document.activeElement !== summary;
      if (active && more.contains(active.card)) stop(false);
      if (focusInside) summary.focus();
    }
  }
  if (more) {
    more.addEventListener('toggle', () => {
      if (!desktop.matches) mobileOpen = more.open;
      syncDisclosure();
    });
    desktop.addEventListener('change', syncViewport);
    syncViewport();
    more.querySelector('[data-shorts-collapse]').addEventListener('click', () => {
      more.open = false;
      syncDisclosure();
      summary.focus();
    });
  }
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
    if (previous.observer) previous.observer.disconnect();
    if (previous.player) previous.player.destroy();
    previous.mount.remove();
    previous.button.remove();
    previous.status.remove();
    delete previous.card.dataset.playing;
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
  function startWithoutCaptions(state, player) {
    if (state.captionDefaultApplied || typeof player.getOptions !== 'function' || typeof player.setOption !== 'function') return;
    try {
      // Apply the opening preference only when the loaded player exposes it.
      // Later changes made with YouTube's own CC control remain the viewer's choice.
      if (player.getOptions('captions').includes('track')) {
        state.captionDefaultApplied = true;
        player.setOption('captions', 'track', {});
      }
    } catch (_) { /* Caption availability must never prevent playback. */ }
  }
  function pauseOutOfView(state) {
    if (active === state && state.player && (!state.inView || document.hidden)) state.player.pauseVideo();
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
    card.insertBefore(button, preview.parentElement);
    card.querySelector('.watch-short-copy').append(status);
    card.dataset.playing = 'true';
    const state = { link, preview, card, mount, button, status, player: null, timer: null, observer: null, inView: true, captionDefaultApplied: false };
    active = state;
    state.timer = setTimeout(() => unavailable(state), 15000);
    // Keep keyboard focus with the player without scrolling to the copy below it.
    button.focus({ preventScroll: true });
    card.scrollIntoView({ block: 'start', behavior: 'instant' });
    if ('IntersectionObserver' in window) {
      state.observer = new IntersectionObserver(entries => {
        if (active !== state) return;
        state.inView = entries.some(entry => entry.isIntersecting);
        pauseOutOfView(state);
      });
      state.observer.observe(preview.parentElement);
    }
    loadAPI().then(YT => {
      if (active !== state) return;
      state.player = new YT.Player(placeholder, {
        width: '100%', height: '100%', videoId: id,
        playerVars: { autoplay: 0, playsinline: 1, rel: 0, cc_load_policy: 0, origin: window.location.origin },
        events: {
          onReady: event => {
            if (active !== state) { event.target.destroy(); return; }
            clearTimeout(state.timer);
            preview.hidden = true;
            mount.dataset.ready = 'true';
            status.textContent = '';
            event.target.getIframe().title = 'YouTube video: ' + card.querySelector('h3').textContent;
            startWithoutCaptions(state, event.target);
            // Only this visitor's explicit click requests playback.
            if (state.inView && !document.hidden) event.target.playVideo();
          },
          onApiChange: event => { if (active === state) startWithoutCaptions(state, event.target); },
          onStateChange: event => {
            if (active !== state || event.data !== 1) return;
            startWithoutCaptions(state, event.target);
            state.captionDefaultApplied = true;
            pauseOutOfView(state);
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
  document.addEventListener('visibilitychange', () => { if (active) pauseOutOfView(active); });
})();
