'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'site-common.js'), 'utf8');
const start = source.indexOf('function ensureConferenceTopicShortcut()');
const end = source.indexOf('function syncDisclosureState(', start);
assert.ok(start >= 0 && end > start);
const implementation = source.slice(start, end);
class Element {
  constructor(tag = 'div', attrs = {}, text = '') {
    this.tag = tag; this.attrs = {...attrs}; this.textContent = text; this.children = [];
    this.classes = new Set((attrs.class || '').split(' ').filter(Boolean));
    this.classList = { contains: c => this.classes.has(c), add: c => this.classes.add(c),
      remove: c => this.classes.delete(c), toggle: (c, active) => active ? this.classes.add(c) : this.classes.delete(c) };
  }
  set href(value) { this.attrs.href = value; } get href() { return this.attrs.href; }
  getAttribute(name) { return this.attrs[name] ?? null; }
  setAttribute(name, value) { this.attrs[name] = value; }
  removeAttribute(name) { delete this.attrs[name]; }
  appendChild(child) { child.parent = this; this.children.push(child); return child; }
  prepend(child) { child.parent = this; this.children.unshift(child); }
  insertAdjacentElement(position, child) {
    assert.equal(position,'afterend'); child.parent=this.parent;
    this.parent.children.splice(this.parent.children.indexOf(this)+1,0,child);
  }
  remove() { this.parent.children = this.parent.children.filter(child => child !== this); }
  descendants() { return this.children.flatMap(child => [child, ...child.descendants()]); }
  querySelectorAll(selector) {
    return this.descendants().filter(n => selector.split(',').some(s => {
      if (s === 'a') return n.tag === 'a';
      if (s === 'a.active') return n.tag === 'a' && n.classes.has('active');
      if (s === 'a[aria-current]') return n.tag === 'a' && 'aria-current' in n.attrs;
      if (s.startsWith('.')) return n.classes.has(s.slice(1));
      if (s.startsWith('[')) return s.slice(1, -1) in n.attrs;
      return false;
    }));
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}
function createHarness(pathname, hash = '') {
  const header = new Element(), desktop = header.appendChild(new Element('div', {class:'nav-links'}));
  const menu = header.appendChild(new Element('div'));
  const isNested = pathname.includes('/answers/'), prefix = isNested ? '../' : '';
  const home = new Element('a', {href:prefix+'index.html'}, 'HOME'); desktop.appendChild(home);
  for (const container of [desktop, menu]) {
    container.appendChild(new Element('a', {href:prefix+'answers.html',class:'active','aria-current':'page'}, 'ANSWERS'));
    container.appendChild(new Element('a', {href:prefix+'art.html'}, 'ART'));
    if (pathname.endsWith('/general-conference.html')) container.appendChild(new Element('a', {href:'general-conference.html',class:'active','aria-current':'page'}, 'GENERAL CONFERENCE'));
    if (pathname.endsWith('/come-follow-me.html')) container.appendChild(new Element('a', {href:'come-follow-me.html',class:'active','aria-current':'page'}, 'COME, FOLLOW ME'));
  }
  const topics = new Element(), head = new Element('head'), listeners = {};
  const location = {pathname, hash};
  const context = {window:{location,addEventListener:(name,fn) => {listeners[name]=fn;}},
    document:{head,createElement:tag => new Element(tag),getElementById:() => menu,
      querySelector:s => s === '.fc-answers-jump-links' ? topics : header},
    relativeAssetHref:p => prefix+p, createConferenceLink:text => new Element('a', {href:'general-conference.html','data-focuschrist-conference-shortcut':'true'},text)};
  vm.createContext(context); vm.runInContext(implementation,context);
  return {context,header,desktop,menu,topics,head,location,listeners};
}
const html = fs.readFileSync(path.join(root,'answers.html'),'utf8');
const pillBlock = html.match(/<div class="fc-answers-jump-links">([\s\S]*?)<\/div>/);
assert.ok(pillBlock,'real Answers topic pills required');
const decode = x => x.replaceAll('&amp;','&').replaceAll('&#39;',"'");
const pills = [...pillBlock[1].matchAll(/<a[^>]*href="([^"]+)"[^>]*>([^<]+)<\/a>/g)].map(m => [decode(m[1]),decode(m[2])]);
assert.equal(pills.length,16,'all sixteen user-visible topic pills are covered');
function check(h,label) {
  const active = h.header.querySelectorAll('a[aria-current]');
  assert.equal(active.length,2,label+': exactly one active link per navigation surface');
  assert.ok(active.every(n => n.classList.contains('active') && n.textContent.toLowerCase() === label.toLowerCase()),label+': label and gold-active class');
  assert.equal(h.desktop.querySelectorAll('[data-focuschrist-current-study]').length,1,label+': current label remains available for collapsed header');
  assert.ok(h.menu.querySelectorAll('a').some(n => /(^|\/)answers\.html$/.test(n.getAttribute('href'))),'Answers parent retained in menu');
  assert.ok(h.desktop.querySelectorAll('a').some(n => /(^|\/)answers\.html$/.test(n.getAttribute('href'))),'Answers parent retained in desktop navigation');
}
for (const [href,label] of pills) {
  const url = new URL(href,'https://focuschrist.com/answers.html');
  const h = createHarness(url.pathname,url.hash);h.context.initCurrentStudyNavigation();check(h,label);
  const size=h.menu.children.length;h.listeners.hashchange();h.listeners.hashchange();
  const desktopSize=h.desktop.children.length;h.listeners.hashchange();
  assert.equal(h.desktop.children.length,desktopSize,'desktop generated topic must not duplicate');
  assert.equal(h.menu.children.length,size,'hash changes must not duplicate generated topic links');check(h,label);
}
for (const [file,label] of [['god-our-heavenly-father.html','God'],['restored-church-of-jesus-christ.html','The Restored Church'],['prayer-and-personal-revelation.html','Prayer & Revelation'],['death-of-a-child.html','Death of a Child'],['divorce-and-faith.html','Divorce'],['look-unto-me-doctrine-and-covenants-6-36.html','Look Unto Me']]) {
  const h=createHarness('/answers/'+file);h.context.initCurrentStudyNavigation();check(h,label);
}
const h=createHarness('/answers.html','#quiet-prayer-title');h.context.initCurrentStudyNavigation();check(h,'Prayer & Revelation');
h.location.hash='#comfort-in-grief-title';h.listeners.hashchange();check(h,'Grief');
h.location.hash='';h.listeners.hashchange();assert.equal(h.desktop.querySelectorAll('a[aria-current]')[0].textContent,'ANSWERS');
assert.equal(h.menu.querySelectorAll('[data-focuschrist-generated-topic]').length,0,'back restores parent without leftover topics');
assert.equal(h.header.classList.contains('fc-has-current-study'),false);
const stand=createHarness('/answers/look-unto-me-doctrine-and-covenants-6-36.html','#stand-forever');stand.context.initCurrentStudyNavigation();check(stand,'Stand Forever');
stand.location.hash='';stand.listeners.hashchange();check(stand,'Look Unto Me');
const cfm=createHarness('/come-follow-me.html');cfm.context.initCurrentStudyNavigation();check(cfm,'Come, Follow Me');
const shortcut=createHarness('/answers.html');shortcut.topics.appendChild(new Element('a',{href:'general-conference.html'},'General Conference'));
shortcut.context.ensureConferenceTopicShortcut();shortcut.context.ensureConferenceTopicShortcut();
assert.equal(shortcut.topics.children.length,1,'existing conference pill must not be duplicated');
shortcut.topics.children=[];shortcut.context.ensureConferenceTopicShortcut();shortcut.context.ensureConferenceTopicShortcut();assert.equal(shortcut.topics.children.length,1);
assert.ok(source.includes('initCurrentStudyNavigation();'),'runtime initializer must invoke topic navigation');
// Links generated after a hash change must close the already initialized menu.
const menuEvents = {}, triggerEvents = {}, documentEvents = {};
const trigger = new Element('button'), liveMenu = new Element();
trigger.hasAttribute = name => name in trigger.attrs;
trigger.addEventListener = (name, fn) => { triggerEvents[name] = fn; };
trigger.focus = () => { trigger.focused = true; };
trigger.contains = node => node === trigger;
liveMenu.addEventListener = (name, fn) => { menuEvents[name] = fn; };
liveMenu.contains = node => node === liveMenu || liveMenu.descendants().includes(node);
const navContext = { window: { toggleMenu() {} }, document: {
  querySelector: () => trigger, getElementById: () => liveMenu,
  addEventListener: (name, fn) => { documentEvents[name] = fn; }
}, MutationObserver: class { observe() {} } };
vm.createContext(navContext);
vm.runInContext(source.slice(source.indexOf('function initNavigation()'), start), navContext);
navContext.initNavigation();
liveMenu.classList.add('show');
const laterLink = liveMenu.appendChild(new Element('a',{href:'#comfort-in-grief-title'},'GRIEF'));
menuEvents.click({target:{closest: selector => selector === 'a' ? laterLink : null}});
assert.equal(liveMenu.classList.contains('show'),false,'delegated click must close a generated topic link');
assert.equal(trigger.getAttribute('aria-expanded'),'false');
liveMenu.classList.add('show');menuEvents.click({target:{closest:() => null}});
assert.equal(liveMenu.classList.contains('show'),true,'non-link menu content must not close the menu');
documentEvents.keydown({key:'Escape'});
assert.equal(liveMenu.classList.contains('show'),false);assert.equal(trigger.focused,true);

// Every pill opens its own page; old bookmarks migrate on load and hashchange.
assert.ok(pills.every(([href]) => !href.includes('#')), 'topic pills must open dedicated pages');
assert.equal(new Set(pills.map(([href]) => href)).size,16,'topic pages must be distinct');
const legacySource = source.slice(source.indexOf('const conferenceLegacyAnchors'),source.indexOf('const RESPECTFUL_QUESTION_RESPONSE'));
for (const [oldPath,oldHash,destination] of [
 ['/answers.html','#quiet-prayer-title','answers/prayer-and-personal-revelation.html'],
 ['/answers.html','#comfort-in-grief-title','answers/grief-and-faith.html'],
 ['/answers.html','#loss-topic','answers/death-of-a-child.html'],
 ['/answers.html','#divorce-topic','answers/divorce-and-faith.html'],
 ['/answers/look-unto-me-doctrine-and-covenants-6-36.html','#stand-forever','stand-forever.html']
]) {
 const replacements=[], listeners=[];
 const location={pathname:oldPath,hash:oldHash,search:'?source=saved',replace:value=>replacements.push(value)};
 vm.runInNewContext(legacySource,{window:{location,addEventListener:(name,fn)=>{if(name==='hashchange')listeners.push(fn);}}});
 assert.deepEqual(replacements,[destination+'?source=saved'],'legacy bookmark forwards with query');
 replacements.length=0;listeners.forEach(fn=>fn());assert.deepEqual(replacements,[destination+'?source=saved']);
 replacements.length=0;location.hash='#unrelated';listeners.forEach(fn=>fn());assert.deepEqual(replacements,[]);
 location.pathname='/ask.html';location.hash=oldHash;listeners.forEach(fn=>fn());assert.deepEqual(replacements,[]);
}

console.log('STUDY NAVIGATION RUNTIME QA PASS: all 16 actual topic pills, article routes, CFM/Conference labels, hash restoration, preserved parent links, and duplicate prevention.');
