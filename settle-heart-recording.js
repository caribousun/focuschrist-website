/* Timestamp links keep the original audio URL as their no-script fallback. */
(() => {
  'use strict';
  const player = document.querySelector('#devotional-recording audio');
  const status = document.getElementById('recording-status');
  if (!player || !status) return;
  let request = 0;
  document.addEventListener('click', event => {
      const link = event.target.closest('a[data-recording-start]');
      if (!link) return;
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const seconds = Number(link.dataset.recordingStart);
      if (!Number.isFinite(seconds) || seconds < 0) return;
      event.preventDefault();
      const currentRequest = ++request;
      const seek = () => {
        if (currentRequest !== request) return;
        player.currentTime = Number.isFinite(player.duration) ? Math.min(seconds, player.duration) : seconds;
      };
      if (player.readyState >= 1) seek();
      else player.addEventListener('loadedmetadata', seek, { once: true });
      status.textContent = 'Loading the recording…';
      document.getElementById('devotional-recording').scrollIntoView({ block: 'start', behavior: 'auto' });
      player.focus({ preventScroll: true });
      Promise.resolve(player.play()).then(() => {
        if (currentRequest !== request) return;
        const time = Math.floor(seconds / 60) + ':' + String(Math.floor(seconds % 60)).padStart(2, '0');
        status.textContent = 'Playing from ' + time + '.';
      }).catch(() => {
        if (currentRequest === request) status.textContent = 'Press Play to listen, or open the original BYU audio below.';
      });
  });
})();
