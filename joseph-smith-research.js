/* One evidence DOM; chapter navigation progressively enhances the full study. */
(function () {
  'use strict';
  const root = document.getElementById('portrait-research');
  if (!root || !document.body.classList.contains('fc-portrait-research-page')) return;
  const sections = Array.from(root.querySelectorAll('.research-part'));
  const chapterCards = Array.from(root.querySelectorAll('.research-chapters > a'));
  let groups;
  try { groups = chapterCards.map(card => JSON.parse(card.dataset.researchSections)); }
  catch (_) { return; } // Invalid metadata leaves the complete no-JS reading path available.
  const sectionNumbers = sections.map(section => Number(section.id.replace('portrait-section-','')));
  const sequence = groups.flat();
  if (!groups.length || groups.some(group => !Array.isArray(group) || !group.length || group.some(n => !Number.isInteger(n))) ||
      sequence.length !== sectionNumbers.length || new Set(sequence).size !== sequence.length ||
      sequence.some((number,index) => number !== sectionNumbers[index]) ||
      chapterCards.some((card,index) => card.getAttribute('href') !== '#portrait-section-'+groups[index][0] || !card.querySelector('strong')?.textContent.trim())) return;
  const labels = chapterCards.map(card => card.querySelector('strong').textContent.trim());
  const switcher = root.querySelector('.research-mode-switch');
  const status = root.querySelector('.research-mode-status');
  const controls = root.querySelector('.research-chapter-controls');
  const previous = root.querySelector('[data-research-previous]');
  const next = root.querySelector('[data-research-next]');
  let active = 0;
  let mode = 'chapters';
  function targetFromHash() {
    try { return document.getElementById(decodeURIComponent(location.hash.slice(1))); }
    catch (_) { return null; }
  }
  function groupOf(node) {
    const section = node && (node.matches('.research-part') ? node : node.closest('.research-part'));
    if (!section) return active;
    const number = Number(section.id.replace('portrait-section-',''));
    return Math.max(0,groups.findIndex(group => group.includes(number)));
  }
  function revealDetails(node) {
    for (let parent=node; parent && parent!==root; parent=parent.parentElement) {
      if (parent.tagName==='DETAILS') parent.open=true;
    }
  }
  function render(scrollToTarget) {
    mode = new URL(location.href).searchParams.get('view')==='all' ? 'all' : 'chapters';
    const target = targetFromHash();
    if (target && root.contains(target)) active = groupOf(target);
    else if (!location.hash || location.hash==='#portrait-research') active=0;
    root.dataset.readingMode=mode;
    root.querySelectorAll('details.research-source-index').forEach(index => {index.open=mode==='all';});
    sections.forEach(section => {
      const number=Number(section.id.replace('portrait-section-',''));
      section.hidden=mode==='chapters' && !groups[active].includes(number);
    });
    switcher.hidden=false;
    switcher.querySelectorAll('button').forEach(button => {
      const selected=button.dataset.researchMode===mode;
      button.setAttribute('aria-pressed',String(selected));
      button.classList.toggle('fc-button--primary',selected);
    });
    root.querySelectorAll('.research-chapters > a').forEach((link,index) => {
      if (mode==='chapters' && index===active) link.setAttribute('aria-current','step');
      else link.removeAttribute('aria-current');
    });
    status.hidden=false;
    status.textContent=mode==='all' ? 'Read all: the complete illustrated research.' : 'Chapter '+(active+1)+' of '+groups.length+': '+labels[active]+'.';
    controls.hidden=mode==='all';
    previous.hidden=active===0;
    next.hidden=active===groups.length-1;
    if (active>0) { previous.href='#portrait-section-'+groups[active-1][0]; previous.textContent='← '+labels[active-1]; }
    if (active<groups.length-1) { next.href='#portrait-section-'+groups[active+1][0]; next.textContent=labels[active+1]+' →'; }
    if (target && root.contains(target)) {
      revealDetails(target);
      if (scrollToTarget) requestAnimationFrame(() => target.scrollIntoView({block:'start',behavior:'instant'}));
    }
  }
  function updateReadingOffset() {
    const header=document.querySelector('.nav');
    const headerBox=header ? header.getBoundingClientRect() : null;
    const headerHeight=headerBox ? Math.max(0,Math.min(headerBox.height,headerBox.bottom)) : 0;
    root.style.setProperty('--research-sticky-top',Math.ceil(headerHeight)+'px');
    root.style.setProperty('--fc-anchor-offset',Math.ceil(headerHeight+switcher.getBoundingClientRect().height+16)+'px');
  }
  function nearestReadingAnchor() {
    const candidates=Array.from(root.querySelectorAll('[data-research-reading-block],.research-source[id]')).filter(node => !node.closest('[hidden]') && node.getClientRects().length);
    let best=null, distance=Infinity;
    candidates.forEach(node => { const d=Math.abs(node.getBoundingClientRect().top-(parseFloat(getComputedStyle(root).getPropertyValue('--fc-anchor-offset'))||120)); if (d<distance) {best=node;distance=d;} });
    return best;
  }
  switcher.addEventListener('click',event => {
    const button=event.target.closest('button[data-research-mode]');
    if (!button) return;
    const anchor=nearestReadingAnchor();
    const url=new URL(location.href);
    if (button.dataset.researchMode==='all') url.searchParams.set('view','all');
    else url.searchParams.delete('view');
    if (anchor) url.hash=anchor.id;
    history.pushState(null,'',url);
    render(true);
  });
  root.addEventListener('click',event => {
    const link=event.target.closest('a[href^="#"]');
    if (!link || event.defaultPrevented || event.button!==0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target=document.getElementById(link.getAttribute('href').slice(1));
    if (!target || !root.contains(target)) return;
    event.preventDefault();
    const url=new URL(location.href);url.hash=target.id;
    history.pushState(null,'',url);render(true);
    if (target.matches('section,.research-reading-block,.research-source')) {
      target.setAttribute('tabindex','-1');target.focus({preventScroll:true});
    }
  });
  // Citation links copied into the shared picture panel return to the source text.
  document.addEventListener('click',event => {
    const link=event.target.closest('#topicArtworkDetailDialog a[href]');
    if (!link || event.defaultPrevented || event.button!==0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const url=new URL(link.href,location.href);
    if (url.origin!==location.origin || url.pathname!==location.pathname || !url.hash) return;
    const target=document.getElementById(url.hash.slice(1));
    if (!target || !root.contains(target)) return;
    event.preventDefault();
    const close=document.querySelector('#topicArtworkDetailDialog [data-topic-art-close]');
    if (close) close.click();
    history.pushState(null,'',url);render(true);
    target.setAttribute('tabindex','-1');target.focus({preventScroll:true});
  });
  window.addEventListener('popstate',() => render(true));
  window.addEventListener('hashchange',() => render(true));
  render(Boolean(location.hash));
  updateReadingOffset();
  if (typeof ResizeObserver!=='undefined') {
    const observer=new ResizeObserver(updateReadingOffset);
    observer.observe(switcher);
    const header=document.querySelector('.nav');if(header)observer.observe(header);
  }
  window.addEventListener('resize',updateReadingOffset);
  let offsetFrame=0;
  window.addEventListener('scroll',() => { if (!offsetFrame) offsetFrame=requestAnimationFrame(() => {offsetFrame=0;updateReadingOffset();}); },{passive:true});
})();
