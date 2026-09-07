(function () {
  'use strict';
  const root = document.getElementById('general-conference');
  if (!root) return;
  const search = root.querySelector('#conference-search');
  const session = root.querySelector('#conference-session');
  const clear = root.querySelector('[data-conference-reset]');
  const status = root.querySelector('[data-conference-status]');
  const empty = root.querySelector('[data-conference-empty]');
  const groups = Array.from(root.querySelectorAll('[data-conference-session]'));
  const cards = Array.from(root.querySelectorAll('[data-conference-talk]'));
  if (!search || !session || !clear || !status || !empty) return;
  const initialOpen = new Map(groups.map(group => [group, group.open]));
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();
  function filter() {
    const words = normalize(search.value).split(/\s+/).filter(Boolean);
    const active = words.length > 0 || session.value !== 'all';
    let count = 0;
    groups.forEach(group => {
      let matches = 0;
      group.querySelectorAll('[data-conference-talk]').forEach(card => {
        const text = normalize(card.dataset.conferenceSearch);
        const match = (session.value === 'all' || group.dataset.conferenceSession === session.value) && words.every(word => text.includes(word));
        card.hidden = !match;
        if (match) matches += 1;
      });
      group.hidden = matches === 0;
      group.open = active ? matches > 0 : initialOpen.get(group);
      count += matches;
    });
    status.textContent = active ? `${count} of ${cards.length} messages match your selection.` : `${cards.length} messages across ${groups.length} sessions. Open a session to browse.`;
    empty.hidden = count !== 0;
    clear.disabled = !active;
  }
  search.addEventListener('input', filter);
  session.addEventListener('change', filter);
  clear.addEventListener('click', () => { search.value = ''; session.value = 'all'; filter(); search.focus(); });
  root.querySelectorAll('[data-conference-clear]').forEach(button => button.addEventListener('click', () => clear.click()));
  root.querySelector('[data-conference-controls]').hidden = false;
  filter();
})();
