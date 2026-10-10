/* Optional device-local bookmarks. No questions, notes, accounts or network calls. */
(function (global) {
  'use strict';
  var KEY = 'focusChrist.savedStudies.v1';
  var LIMIT = 50;
  var ROUTES = new Set(['/history/emma-hale-smith.html', '/answers.html', '/atonement.html', '/art-study/be-still.html', '/answers/faith-in-jesus-christ-during-trials.html', '/answers/prayer-and-personal-revelation.html', '/answers/look-unto-me-doctrine-and-covenants-6-36.html']);
  function normalize(raw, origin) {
    if (typeof raw !== 'string' || raw.length > 600) return null;
    try {
      var u = new URL(raw, origin + '/');
      if (u.origin !== origin || !/^https?:$/.test(u.protocol) || u.username || u.password || u.search || !ROUTES.has(u.pathname)) return null;
      var fragment = decodeURIComponent(u.hash.slice(1));
      if (fragment && !/^[a-zA-Z0-9_-]+$/.test(fragment)) return null;
      return u.pathname + (fragment ? '#' + fragment : '');
    } catch (_) { return null; }
  }
  function createStore(getStorage, origin) {
    function read() {
      try {
        var raw = getStorage().getItem(KEY);
        if (raw === null) return {ok:true, items:[]};
        var data = JSON.parse(raw);
        if (!data || data.version !== 1 || !Array.isArray(data.items) || data.items.length > LIMIT) throw new Error('format');
        var seen = new Set();
        var items = data.items.map(function (item) {
          var url = item && normalize(item.url, origin);
          if (!url || typeof item.title !== 'string' || !item.title.trim() || item.title.length > 160 || seen.has(url)) throw new Error('entry');
          seen.add(url); return {url:url, title:item.title};
        });
        return {ok:true, items:items};
      } catch (_) { return {ok:false, items:[], message:'Saved studies could not be read. Browser storage may be unavailable or the saved list may be damaged. Clear the list to try again.'}; }
    }
    function write(items) {
      try {
        var text = JSON.stringify({version:1, items:items});
        var storage = getStorage(); storage.setItem(KEY, text);
        if (storage.getItem(KEY) !== text) throw new Error('readback');
        return {ok:true, items:items};
      } catch (_) { return {ok:false, message:'Your change was not saved. Browser storage may be blocked or full. You can still use every study link.'}; }
    }
    return {
      read:read,
      save:function (url, title) {
        url = normalize(url, origin);
        if (!url || typeof title !== 'string' || !title.trim() || title.length > 160) return {ok:false, message:'This study link cannot be saved.'};
        var state = read(); if (!state.ok) return state;
        if (state.items.some(function (x) { return x.url === url; })) return {ok:true, items:state.items, message:'This study is already saved.'};
        if (state.items.length >= LIMIT) return {ok:false, message:'Your list holds 50 studies. Remove one before saving another.'};
        var result = write(state.items.concat([{url:url, title:title.trim()}]));
        if (result.ok) result.message = 'Study saved in this browser.';
        return result;
      },
      remove:function (url) {
        var state = read(); if (!state.ok) return state;
        var result = write(state.items.filter(function (x) { return x.url !== url; }));
        if (result.ok) result.message = 'Study removed.'; return result;
      },
      clear:function () {
        try { var storage = getStorage(); storage.removeItem(KEY); if (storage.getItem(KEY) !== null) throw new Error('readback'); return {ok:true, items:[], message:'Saved studies cleared.'}; }
        catch (_) { return {ok:false, message:'The list could not be cleared. Browser storage may be unavailable.'}; }
      }
    };
  }
  function mount(doc, win) {
    var panels = Array.from(doc.querySelectorAll('[data-saved-studies]'));
    var store = createStore(function () { return win.localStorage; }, win.location.origin);
    function announce(message) { doc.querySelectorAll('[data-saved-status]').forEach(function (n) { n.textContent = message || ''; }); }
    function render(message) {
      var state = store.read();
      panels.forEach(function (panel) {
        var list = panel.querySelector('[data-saved-list]'); list.replaceChildren();
        state.items.forEach(function (item) {
          var li = doc.createElement('li'), a = doc.createElement('a'), button = doc.createElement('button');
          a.href = item.url; a.textContent = item.title;
          button.type = 'button'; button.className = 'fc-button'; button.textContent = 'Remove'; button.setAttribute('aria-label', 'Remove ' + item.title);
          button.addEventListener('click', function () {
            var result = store.remove(item.url); render(result.message);
            var next = list.querySelector('button') || panel.querySelector('[data-clear-saved]'); if (next) next.focus();
          });
          li.append(a, button); list.append(li);
        });
        panel.querySelector('[data-saved-empty]').hidden = !state.ok || state.items.length > 0;
      });
      announce(!state.ok ? state.message : (message || ''));
    }
    doc.querySelectorAll('[data-save-study]').forEach(function (button) {
      button.hidden = false;
      button.addEventListener('click', function () { var result = store.save(button.dataset.saveStudy, button.dataset.studyTitle); render(result.message); });
    });
    doc.querySelectorAll('[data-clear-saved]').forEach(function (button) { button.hidden = false; button.addEventListener('click', function () { var result = store.clear(); render(result.message); }); });
    win.addEventListener('storage', function (event) { if (event.key === KEY || event.key === null) render('Saved studies updated in this browser.'); });
    render();
  }
  var api = {key:KEY, normalize:normalize, createStore:createStore, mount:mount};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (global.document) { if (global.document.readyState === 'loading') global.document.addEventListener('DOMContentLoaded', function () { mount(global.document, global); }); else mount(global.document, global); }
})(typeof window === 'undefined' ? globalThis : window);
