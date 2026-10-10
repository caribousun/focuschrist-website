// Study actions must work for every original picture and the separate Eleazer hero.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
function setup(markup, url) {
  const dom = new JSDOM(markup, { url, runScripts: 'outside-only' });
  const w = dom.window;
  w.TextEncoder = TextEncoder; const frames = new Map(); let frameId = 0; w.requestAnimationFrame = fn => { frames.set(++frameId, fn); return frameId; }; w.cancelAnimationFrame = id => frames.delete(id); const tickFrames = () => { const batch = [...frames.values()]; frames.clear(); batch.forEach(fn => fn()); };
  w.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
  w.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new w.Event('close')); };
  w.HTMLElement.prototype.scrollIntoView = function () {};
  w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
  w.tickFrames = tickFrames;
  for (const file of ['site-common.js', 'full-image-viewer.js', 'topic-artwork-details.js']) w.eval(read(file));
  w.document.dispatchEvent(new w.Event('DOMContentLoaded'));
  return dom;
}
const fixture = setup('<main><section><h2 id="reading">History</h2><figure><a href="/picture.webp"><img src="/picture.webp" alt="Study"></a><figcaption><h3>Record</h3><p>A historical source.</p><a href="https://history.churchofjesuschrist.org/chd/individual/eleazer-miller-1795">Official biography</a><a href="https://history.churchofjesuschrist.org.evil.example/record">Wrong host</a><a href="http://history.churchofjesuschrist.org/record">Insecure</a><a href="https://ensignpeakfoundation.org/moyle-park-alpine-utah/">Moyle Park</a><a href="http://ensignpeakfoundation.org/moyle-park-alpine-utah/">Insecure park</a><a href="https://www.ensignpeakfoundation.org/moyle-park-alpine-utah/">Unapproved subdomain</a><a href="https://ensignpeakfoundation.org.evil.example/moyle-park-alpine-utah/">Lookalike park</a></figcaption></figure></section></main>', 'https://focuschrist.com/history/test.html');
fixture.window.document.querySelector('figure>a').click();
assert.deepEqual([...fixture.window.document.querySelectorAll('[data-topic-art-source]')].map(a => a.hostname), ['history.churchofjesuschrist.org', 'ensignpeakfoundation.org']);
fixture.window.close();
const fourSources = '<body class="fc-life-story"><main><section><h2>Reading</h2><figure><a href="/picture.webp"><img src="/picture.webp" alt="Study"></a><figcaption><h3>Sources</h3><p>Read the records.</p>' + [1, 2, 3, 4].map(n => `<a href="https://www.churchofjesuschrist.org/source-${n}">Source ${n}</a>`).join('') + '</figcaption></figure></section></main></body>';
const outsideStory = setup(fourSources, 'https://focuschrist.com/history/unapproved.html');
outsideStory.window.document.querySelector('figure>a').click();
assert.equal(outsideStory.window.document.querySelectorAll('[data-topic-art-source]').length, 3, 'Four-source exception must not expand to other pages');
outsideStory.window.close();
const researchHosts = ['saintsbysea.byu.edu', 'rsc.byu.edu', 'www.churchhistorianspress.org', 'www.fairlatterdaysaints.org'];
for (const route of ['john-tanner', 'eleazer-miller', 'john-rowe-moyle', 'unapproved']) {
  for (const bodyClass of ['fc-life-story', 'unapproved']) {
    const links = researchHosts.flatMap(host => [`https://${host}/record`, `http://${host}/record`, `https://sub.${host}/record`, `https://${host}.evil.example/record`]);
    const markup = '<body class="'+bodyClass+'"><main><section><h2>Record</h2><figure><a href="/picture.webp"><img src="/picture.webp" alt="Study"></a><figcaption><h3>Historical sources</h3><p>Read the record.</p>'+links.map(url => `<a href="${url}">Historical record</a>`).join('')+'</figcaption></figure></section></main></body>';
    const d = setup(markup, `https://focuschrist.com/history/${route}.html`);
    d.window.document.querySelector('figure>a').click();
    assert.deepEqual([...d.window.document.querySelectorAll('[data-topic-art-source]')].map(a => a.hostname), route !== 'unapproved' && bodyClass === 'fc-life-story' ? researchHosts : [], 'Research hosts require exact approved History route and body class; HTTPS and exact host only');
    d.window.close();
  }
}
const journal = 'https://catalog.churchofjesuschrist.org/assets/994fb2fe-d8b1-4156-a452-3a8fecacf538/1/42';
for (const route of ['john-tanner', 'eleazer-miller', 'unapproved']) {
 for (const body of ['fc-life-story', 'unapproved']) {
  const urls=[journal,journal.replace('/42','/43'),journal.replace('https:','http:'),journal.replace('catalog.','sub.catalog.'),journal+'?other=1'];
  const markup='<body class="'+body+'"><main><figure><a href="/picture.webp"><img src="/picture.webp" alt="Record"></a><figcaption><h3>Journal</h3><p>Primary record.</p>'+urls.map(url=>`<a href="${url}">Journal</a>`).join('')+'</figcaption></figure></main></body>';
  const d=setup(markup,`https://focuschrist.com/history/${route}.html`);d.window.document.querySelector('figure>a').click();
  assert.deepEqual([...d.window.document.querySelectorAll('[data-topic-art-source]')].map(a=>a.href),route==='john-tanner'&&body==='fc-life-story'?[journal]:[],'Only exact Tanner journal URL in its owning story is permitted');d.window.close();
 }
}
const biography = 'https://www.gutenberg.org/cache/epub/46734/pg46734-images.html';
for (const route of ['john-tanner', 'eleazer-miller', 'john-rowe-moyle', 'unapproved']) {
 for (const body of ['fc-life-story', 'unapproved']) {
  const urls = [biography, biography.replace('https:', 'http:'), biography.replace('www.gutenberg.org', 'gutenberg.org'), biography.replace('www.gutenberg.org', 'www.gutenberg.org.evil.example'), biography.replace('www.gutenberg.org', 'sub.www.gutenberg.org'), biography.replace('46734-images', '46734'), biography + '?other=1', biography + '#other'];
  const markup = '<body class="'+body+'"><main><figure><a href="/picture.webp"><img src="/picture.webp" alt="Record"></a><figcaption><h3>Biography</h3><p>Historical record.</p>'+urls.map(url=>`<a href="${url}">Biography</a>`).join('')+'</figcaption></figure></main></body>';
  const d = setup(markup, `https://focuschrist.com/history/${route}.html`);
  d.window.document.querySelector('figure>a').click();
  assert.deepEqual([...d.window.document.querySelectorAll('[data-topic-art-source]')].map(a=>a.href), route === 'john-tanner' && body === 'fc-life-story' ? [biography] : [], 'Only exact HTTPS Tanner biography URL in its owning story/body is permitted');
  d.window.close();
 }
}
if (!process.argv.includes('--source-host-only')) {
  const allStories = ['john-tanner', 'eleazer-miller', 'john-rowe-moyle'];
  const storyOption = process.argv.indexOf('--story');
  const selected = storyOption < 0 ? allStories : [process.argv[storyOption + 1]];
  assert(selected.every(slug => allStories.includes(slug)));
  for (const slug of selected) {
    const dom = setup(read(`history/${slug}.html`), `https://focuschrist.com/history/${slug}.html`);
    const d = dom.window.document;
    assert.equal(new URL(d.querySelector('[data-focuschrist-art-gallery]').href).pathname, '/art.html', 'History footer must use the approved Art opening');
    assert.equal(new URL(d.querySelector('[data-focuschrist-evidences]').href).pathname, '/book-of-mormon-evidences.html');
    assert.equal(new URL(d.querySelector('[data-focuschrist-scripture-library]').src).pathname, '/scripture-library.js');
    for (const a of d.querySelectorAll('nav[data-focuschrist-header] a[href]')) {
      const url = new URL(a.href);
      if (url.origin === 'https://focuschrist.com' && /\.html$/.test(url.pathname)) assert(fs.existsSync(path.join(root, url.pathname)), 'Broken runtime navigation: ' + url.pathname);
    }
    const pictures = [...d.querySelectorAll('main figure>a')];
    assert.equal(pictures.length, { 'john-tanner': 10, 'eleazer-miller': 11, 'john-rowe-moyle': 10 }[slug]);
    const story = JSON.parse(read('docs/history-stories/stories.json')).stories.find(item => item.id === slug);
    const expectedIds = [...(slug === 'eleazer-miller' ? ['miller-teaching-brigham'] : []), ...story.units.map(unit => unit.id)];
    assert.deepEqual(pictures.map(a => a.closest('figure').dataset.exclusiveArtwork), expectedIds, 'Preserve every original picture in order with only the distinct Eleazer hero added');
    assert.equal(new Set(pictures.map(a => a.href)).size, pictures.length, 'Every picture must open its own unique original');
    assert.equal(pictures.filter(a => a.classList.contains('fc-visual-hero')).length, 1);
    for (const trigger of pictures) {
      trigger.focus(); trigger.click();
      const panel = d.getElementById('topicArtworkDetailDialog');
      assert(panel.open);
      assert(panel.querySelector('[data-topic-art-source]'), 'Every original has a real source');
      const expectedSources = [...trigger.closest('figure').querySelectorAll('figcaption .fc-study-visual-sources a')].map(a => a.href);
      assert.deepEqual([...panel.querySelectorAll('[data-topic-art-source]')].map(a => a.href), expectedSources, 'Every historical source remains accessible inside its picture study');
      assert.equal(panel.querySelector('h2').textContent, trigger.closest('figure').querySelector('h3').textContent);
      const full = panel.querySelector('[data-full-image-viewer]');
      full.focus(); full.click();
      const viewer = d.querySelector('.fc-full-image-viewer');
      assert(viewer.open && panel.open);
      viewer.querySelector('button').click();
      assert(!viewer.open && panel.open);
      assert.equal(d.activeElement, full);
      panel.querySelector('[data-topic-art-close]').click();
      assert.equal(d.activeElement, trigger);
      trigger.click();
      const next = panel.querySelector('[data-topic-art-continue]');
      const target = d.getElementById(new URL(next.href).hash.slice(1));
      assert.equal(target.closest('section'), trigger.closest('section'));
      next.click(); dom.window.tickFrames(); dom.window.tickFrames(); assert.equal(d.activeElement, target);
    }
    dom.window.close();
  }
}
console.log('PASS: exact official history host; story picture study/full-size/source/focus/Continue contracts');
