(function () {
  'use strict';
  var active = null;
  function cleanup() {
    if (active) active.remove();
    active = null;
    document.body.classList.remove('fc-printing-companion');
  }
  document.querySelectorAll('[data-print-study]').forEach(function (button) {
    button.hidden = false;
    button.addEventListener('click', function () {
      cleanup();
      var source = Array.from(document.querySelectorAll('[data-print-companion]')).find(function (item) { return item.dataset.printCompanion === button.dataset.printStudy; });
      if (!source) return;
      active = source.cloneNode(true);
      active.className = 'fc-print-copy';
      active.removeAttribute('data-print-companion');
      active.querySelectorAll('[id]').forEach(function (el) { el.removeAttribute('id'); });
      document.body.append(active);
      document.body.classList.add('fc-printing-companion');
      try { window.print(); } catch (_) { cleanup(); }
    });
  });
  window.addEventListener('afterprint', cleanup);
  window.addEventListener('pagehide', cleanup);
})();
