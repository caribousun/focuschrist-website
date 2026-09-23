'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM, VirtualConsole} = require('jsdom');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'watch.html'), 'utf8');
const script = fs.readFileSync(path.join(root, 'watch-shorts.js'), 'utf8');
const records = JSON.parse(fs.readFileSync(path.join(root, 'docs/watch-shorts.json'), 'utf8')).shorts;
const flush = async () => { await Promise.resolve(); await Promise.resolve(); await Promise.resolve(); };
function setup() {
  const dom = new JSDOM(html, {url:'https://focuschrist.com/watch.html', runScripts:'outside-only', virtualConsole:new VirtualConsole()});
  const w = dom.window, d = w.document, players = [], timers = new Map();
  const scrolls = [], focusCalls = [];
  w.HTMLElement.prototype.scrollIntoView = function(options) { scrolls.push({node:this, options}); };
  const nativeFocus = w.HTMLElement.prototype.focus;
  w.HTMLElement.prototype.focus = function(options) { focusCalls.push({node:this, options}); nativeFocus.call(this, options); };
  let timerId = 0;
  w.setTimeout = (callback, delay) => { timers.set(++timerId, {callback, delay}); return timerId; };
  w.clearTimeout = id => timers.delete(id);
  function Player(element, options) {
    this.options = options; this.destroyed = false; this.plays = 0;
    this.frame = d.createElement('iframe');
    this.frame.src = 'https://www.youtube.com/embed/' + options.videoId;
    element.replaceWith(this.frame);
    this.getIframe = () => this.frame;
    this.playVideo = () => { this.plays++; };
    this.destroy = () => { this.destroyed = true; this.frame.remove(); };
    this.ready = () => options.events.onReady({target:this});
    this.error = () => options.events.onError({target:this, data:100});
    players.push(this);
  }
  const section = d.querySelector('[data-watch-shorts]');
  const links = [...section.querySelectorAll('.watch-short-preview[data-short-play]')];
  const click = (i, extras={}) => {
    const event = new w.MouseEvent('click', {bubbles:true, cancelable:true, button:0, ...extras});
    links[i].dispatchEvent(event); return event;
  };
  const api = async () => { w.YT = {Player}; w.onYouTubeIframeAPIReady(); await flush(); };
  const timeout = () => { const pending = [...timers.values()]; timers.clear(); pending.forEach(t => { assert.equal(t.delay,15000); t.callback(); }); };
  w.eval(script);
  return {dom,w,d,players,timers,section,links,click,api,timeout,scrolls,focusCalls,close:()=>dom.window.close()};
}
(async () => {
  let h = setup();
  assert.equal(h.section.querySelectorAll('[data-short-play]').length,8);
  assert.equal(h.section.querySelectorAll('iframe').length,0);
  assert.equal(h.d.querySelectorAll('script[src="https://www.youtube.com/iframe_api"]').length,0,'No API or player on initial load');
  assert.equal(h.click(0).defaultPrevented,true);
  assert.equal(h.links[0].hidden,false,'Poster stays visible while API is pending');
  assert.equal(h.d.activeElement,h.section.querySelector('.watch-short-stop'));
  assert.equal(h.d.querySelectorAll('script[src="https://www.youtube.com/iframe_api"]').length,1);
  const close = h.section.querySelector('.watch-short-stop'), media = h.links[0].parentElement;
  assert.equal(close.nextElementSibling,media,'Close precedes the media, not the copy below');
  assert.equal(h.focusCalls.at(-1).node,close);
  assert.equal(h.focusCalls.at(-1).options.preventScroll,true,'Focusing Close cannot scroll below the player');
  assert.equal(h.scrolls[0].node,media.parentElement,'Opening deliberately scrolls the owning card');
  assert.equal(h.scrolls[0].options.block,'start');
  assert.equal(media.parentElement.dataset.playing,'true');
  await h.api();
  const first = h.players[0];
  assert.equal(first.options.videoId,records[0].id);
  assert.equal(first.options.playerVars.autoplay,0);
  assert.equal(first.options.playerVars.origin,'https://focuschrist.com');
  assert.equal(first.plays,0);
  assert.equal(h.links[0].hidden,false,'Poster remains until readiness');
  first.ready();
  assert.equal(first.plays,1,'Only explicit requested player plays after readiness');
  assert.equal(h.links[0].hidden,true);
  assert.equal(h.section.querySelector('.watch-short-player').dataset.ready,'true');
  assert.equal(first.frame.title,'YouTube video: '+records[0].title);
  h.click(1); await flush();
  assert.equal(first.destroyed,true);
  assert.equal(h.links[0].closest('.watch-short').hasAttribute('data-playing'),false,'Switch restores previous card layout');
  assert.equal(h.section.querySelectorAll('[data-playing]').length,1);
  assert.equal(h.section.querySelectorAll('iframe').length,1,'Switch retains only one player');
  assert.equal(h.links[0].hidden,false);
  h.players[1].ready();
  first.error(); first.ready();
  assert.equal(h.section.querySelectorAll('iframe').length,1,'Stale callbacks cannot stop current player');
  h.section.querySelector('.watch-short-stop').click();
  assert.equal(h.section.querySelectorAll('iframe').length,0);
  assert.equal(h.d.activeElement,h.links[1]);
  assert.equal(h.section.querySelectorAll('[data-playing]').length,0,'Close restores resting layout');
  h.click(2); await flush(); h.players[2].ready();
  h.section.querySelector('.watch-short-stop').dispatchEvent(new h.w.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));
  assert.equal(h.section.querySelectorAll('iframe').length,0);
  assert.equal(h.d.activeElement,h.links[2]);
  for (const extras of [{ctrlKey:true},{metaKey:true},{shiftKey:true},{altKey:true},{button:1}]) {
    assert.equal(h.click(0,extras).defaultPrevented,false);
    assert.equal(h.section.querySelectorAll('.watch-short-player').length,0);
  }
  h.links[0].dataset.shortPlay='bad/path?id';
  assert.equal(h.click(0).defaultPrevented,false);
  assert.equal(h.section.querySelectorAll('.watch-short-player').length,0);
  h.click(3); await flush(); h.w.dispatchEvent(new h.w.Event('pagehide'));
  assert.equal(h.section.querySelectorAll('iframe').length,0);
  assert.equal(h.timers.size,0); h.close();

  h=setup();
  const textTrigger=h.section.querySelector('.watch-short-open');
  textTrigger.dispatchEvent(new h.w.MouseEvent('click',{bubbles:true,cancelable:true,button:0}));
  await h.api();
  assert.equal(h.players[0].options.videoId,records[0].id,'Text and image triggers select same video');
  assert.equal(h.players[0].frame.closest('.watch-short-media'),h.links[0].parentElement,'Text trigger mounts player in image media region');
  h.players[0].ready();
  assert.equal(h.links[0].hidden,true,'Text trigger hides image poster after readiness');
  assert.equal(textTrigger.hidden,false);
  h.section.querySelector('.watch-short-stop').click();
  assert.equal(h.d.activeElement,textTrigger,'Close restores original text trigger');
  assert.equal(h.links[0].hidden,false);
  h.click(0);await flush();h.players[1].ready();
  assert.equal(h.players[1].options.videoId,records[0].id);
  h.section.querySelector('.watch-short-stop').click();
  assert.equal(h.d.activeElement,h.links[0],'Image-trigger Close restores image trigger');h.close();

  h=setup(); h.click(0); h.click(1);
  assert.equal(h.d.querySelectorAll('script[src="https://www.youtube.com/iframe_api"]').length,1);
  await h.api();
  assert.equal(h.players.length,1,'Pending switch never constructs obsolete player');
  assert.equal(h.players[0].options.videoId,records[1].id);
  h.section.querySelector('.watch-short-stop').click(); h.players[0].ready();
  assert.equal(h.section.querySelectorAll('iframe').length,0,'Ready after pending close never resurrects player');
  assert.equal(h.players[0].plays,0); assert.equal(h.d.activeElement,h.links[1]); h.close();

  h=setup(); h.click(0); h.section.querySelector('.watch-short-stop').click(); await h.api();
  assert.equal(h.players.length,0,'Close before API completion cancels creation'); h.close();

  for (const mode of ['api-error','api-timeout','player-error','player-timeout']) {
    h=setup(); h.click(0);
    if(mode.startsWith('player')) await h.api();
    if(mode==='api-error') { h.d.querySelector('script[src="https://www.youtube.com/iframe_api"]').dispatchEvent(new h.w.Event('error')); await flush(); }
    else if(mode==='player-error') h.players[0].error();
    else h.timeout();
    assert.equal(h.section.querySelectorAll('iframe,.watch-short-player,.watch-short-stop').length,0,mode+' cleans player and controls');
    assert.equal(h.links[0].hidden,false);
    assert.equal(h.section.querySelectorAll('[data-playing]').length,0,mode+' restores resting layout');
    assert.equal(h.d.activeElement,h.links[0]);
    assert.match(h.section.querySelector('.watch-short-status').textContent,/watch this Short on YouTube/);
    assert.equal(h.timers.size,0);
    if(mode==='api-timeout') { await h.api(); assert.equal(h.players.length,0,'Late API callback after timeout cannot create player'); }
    if(mode==='player-timeout') { h.players[0].ready(); assert.equal(h.players[0].plays,0); }
    h.close();
  }
  console.log('Watch Shorts official API runtime PASS: no-load player, pending/readiness, one-player switching, stale callbacks, close/Escape/focus, modifier fallback, invalid ID, API/player failure/timeout and pagehide');
})().catch(error=>{console.error(error);process.exitCode=1;});
