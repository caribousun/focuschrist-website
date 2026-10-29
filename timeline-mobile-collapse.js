/* Mobile-only disclosures; desktop retains the existing visible controls. */
(function () {
  'use strict';
  const viewer = document.getElementById('viewer');
  const viewToggle = document.getElementById('mobileViewToggle');
  const playbackToggle = document.getElementById('mobilePlaybackToggle');
  const viewControls = document.getElementById('mobileViewControls');
  const playbackControls = document.getElementById('mobilePlaybackControls');
  const yearLabel = document.getElementById('yearLabel');
  if (!viewer || !viewToggle || !playbackToggle || !viewControls || !playbackControls || !yearLabel || !window.matchMedia) return;

  const mobile = window.matchMedia('(max-width:900px)');
  const panels = [
    { button: viewToggle, controls: viewControls, expanded: false, fallback: () => document.querySelector('.view-switch button.on') },
    { button: playbackToggle, controls: playbackControls, expanded: false, fallback: () => document.getElementById('playBtn') }
  ];
  function syncLabels() {
    const mode = document.querySelector('.view-switch button.on');
    viewToggle.textContent = 'View and filters · ' + (mode ? mode.textContent.trim() : 'Timeline');
    playbackToggle.textContent = 'Playback · ' + yearLabel.textContent.trim();
  }
  function syncLayout() {
    panels.forEach(panel => {
      const active = document.activeElement;
      const losingContentFocus = mobile.matches && !panel.expanded && panel.controls.contains(active);
      const losingToggleFocus = !mobile.matches && active === panel.button;
      panel.controls.hidden = mobile.matches && !panel.expanded;
      panel.button.hidden = !mobile.matches;
      panel.button.setAttribute('aria-expanded', String(!mobile.matches || panel.expanded));
      if (losingContentFocus) panel.button.focus({ preventScroll: true });
      if (losingToggleFocus) {
        const target = panel.fallback();
        if (target) target.focus({ preventScroll: true });
      }
    });
    syncLabels();
  }
  panels.forEach(panel => panel.button.addEventListener('click', () => {
    if (!mobile.matches) return;
    panel.expanded = !panel.expanded;
    syncLayout();
  }));
  if (mobile.addEventListener) mobile.addEventListener('change', syncLayout);
  else if (mobile.addListener) mobile.addListener(syncLayout);
  new MutationObserver(syncLabels).observe(viewControls, { subtree: true, attributes: true, attributeFilter: ['class'] });
  new MutationObserver(syncLabels).observe(yearLabel, { subtree: true, childList: true, characterData: true });
  syncLayout();
})();
