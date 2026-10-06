/* Shared first-screen invitation. Required text stays in normal document flow. */
(() => {
  function init() {
    const hero = document.querySelector('.fc-visual-hero,[data-covenant-hero-slot],.cfm-desktop-picture,.gc-intro-visual');
    if (!hero) return;
    const opening = document.querySelector('.fc-life-opening,.jj-opening,.fc-topic-opening .fc-page-intro,.fc-page-intro,.cfm-hero__copy,.gc-page-opening > div,.joseph-bridge-intro,.research-opening');
    if (!opening || opening.hasAttribute('data-unified-opening')) return;
    opening.setAttribute('data-unified-opening', '');
    const briefDescriptions = {
      '/answers/stand-forever.html': 'Study foundational questions, honest inquiry, and revelation.',
      '/answers/settle-this-in-your-hearts.html': 'Deepen your faith in Jesus Christ through daily discipleship.'
    };
    const brief = briefDescriptions[location.pathname];
    if (brief && !opening.querySelector('.fc-page-intro-copy,.fc-topic-subtitle')) {
      const title = opening.querySelector('h1');
      if (title) {
        const description = document.createElement('p');
        description.className = 'fc-page-intro-copy';
        description.textContent = brief;
        title.after(description);
      }
    }
    const authoredCue = opening.querySelector('.timeline-opening-continue');
    const cue = authoredCue || document.createElement('a');
    if (!authoredCue) {
      cue.className = 'fc-unified-continue';
      cue.innerHTML = 'Continue <span aria-hidden="true">\u2193</span>';
    }
    const scope = opening.closest('.cfm-hero,.gc-page-opening') || opening;
    if (scope !== opening) scope.setAttribute('data-unified-shell', '');
    const previous = [...scope.querySelectorAll('.fc-scroll-cue,.fc-mobile-scroll-cue,.fc-art-continue,.fc-covenant-continue')].filter(el => el !== authoredCue);
    previous.forEach(el => el.setAttribute('data-unified-old-cue', ''));
    const extras = [...opening.querySelectorAll('.fc-actions,.cfm-actions,.fc-conference-actions,.fc-life-directory,.fc-page-intro-scripture,.fc-conference-lead,.gc-stats,.fc-father-opening-guide')];
    const copyContainer = opening.querySelector('.fc-container--standard');
    if (copyContainer) {
      if (copyContainer.querySelector('.fc-page-intro-copy')) extras.push(...copyContainer.querySelectorAll('.fc-topic-subtitle'));
      extras.push(...[...copyContainer.children].filter(el => el.tagName === 'P' && !el.className));
    }
    let continuation;
    const origins = new WeakMap();
    const retain = el => {
      if (!origins.has(el)) { const marker = document.createComment("Original introduction position"); el.before(marker); origins.set(el, marker); }
      if (!continuation) {
        continuation = document.createElement('section');
        continuation.className = 'fc-unified-opening-continuation';
        continuation.id = 'fc-opening-retained';
        continuation.setAttribute('aria-label', 'Continue the introduction');
        (opening.closest('.fc-topic-opening,.cfm-hero,.gc-page-opening') || opening).after(continuation);
      }
      continuation.append(el);
      [...continuation.children].sort((a,b) => origins.get(a).compareDocumentPosition(origins.get(b)) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1).forEach(node => continuation.append(node));
    };
    extras.forEach(retain);
    opening.append(cue);
    const mobile = matchMedia('(max-width:700px)');
    function destination() {
      const old = previous.find(el => mobile.matches ? el.matches('.fc-mobile-scroll-cue') : !el.matches('.fc-mobile-scroll-cue')) || previous[0];
      const josephStarts = {'/joseph-smith-likeness.html':'#joseph-study-entrance','/joseph-smith-portrait-research.html':'#portrait-section-1'};
      const explicitStart = josephStarts[location.pathname];
      let href = explicitStart && document.getElementById(explicitStart.slice(1)) ? explicitStart : old && old.getAttribute('href');
      if (!href) {
        const action = opening.querySelector('a[href^="#"]:not(.fc-unified-continue)');
        href = action && action.getAttribute('href');
      }
      if (!href) {
        let next = opening.nextElementSibling || opening.parentElement.nextElementSibling;
        while (next && next.matches('script,style,link')) next = next.nextElementSibling;
        if (next) { if (!next.id) next.id = 'fc-opening-study'; href = '#' + next.id; }
      }
      if (continuation && continuation.children.length) {
        const target = href && document.getElementById(href.slice(1));
        const existingComesFirst = target && (target.contains(continuation) || (target.compareDocumentPosition(continuation) & Node.DOCUMENT_POSITION_FOLLOWING));
        if (!existingComesFirst) href = '#' + continuation.id;
      }
      if (href) cue.setAttribute('href', href);
    }
    const optional = opening.matches('.jj-opening') ? [] : [...opening.querySelectorAll('.fc-page-intro-copy,.fc-opening-explanation,.joseph-bridge-intro > p:last-of-type,.research-opening > p:last-of-type')].map(el => { const marker = document.createComment('Retained opening description'); el.before(marker); return {el,marker}; });
    let queued = false;
    function measure() {
      queued = false;
      optional.forEach(({el,marker}) => marker.after(el));
      opening.style.setProperty('--unified-opening-border', getComputedStyle(opening).borderBottomWidth);
      const top = opening.getBoundingClientRect().top + scrollY;
      const value = `${top}px`;
      if (opening.style.getPropertyValue('--unified-opening-top') !== value) opening.style.setProperty('--unified-opening-top', value);
      for (const {el} of optional) {
        if (cue.getBoundingClientRect().bottom + scrollY > innerHeight - 20 + 1) retain(el);
      }
      if (continuation) continuation.hidden = !continuation.children.length;
      destination();
    }
    const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(measure); } };
    window.addEventListener('resize', schedule);
    window.addEventListener('pageshow', schedule);
    mobile.addEventListener('change', schedule);
    if (document.fonts) document.fonts.ready.then(schedule);
    if (window.ResizeObserver) {
      const observer = new ResizeObserver(schedule);
      document.querySelectorAll('.nav,.fc-visual-hero,[data-covenant-hero-slot]').forEach(el => { if (!opening.contains(el)) observer.observe(el); });
    }
    measure();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
