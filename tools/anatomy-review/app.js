(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const pointSets = { arm: ['shoulder', 'elbow', 'wrist', 'index_mcp', 'little_mcp', 'thumb_base'], leg: ['hip', 'knee', 'ankle', 'heel', 'big_toe', 'little_toe'] };
  const currentPoints = () => pointSets[limb().type || 'arm'] || pointSets.arm;
  const labels = { shoulder: 'Shoulder', elbow: 'Elbow', wrist: 'Wrist', index_mcp: 'Index knuckle', little_mcp: 'Little-finger knuckle', thumb_base: 'Thumb base', hip: 'Hip', knee: 'Knee', ankle: 'Ankle', heel: 'Heel', big_toe: 'Big toe', little_toe: 'Little toe' };
  const checkLabels = { whole_chain: 'I traced the whole limb back to its person.', hand_ownership: 'I checked which person owns each visible hand.', digits_and_thumb: 'I inspected visible digits and thumb placement.', contact_and_overlap: 'I inspected grip, contact, and front-to-back overlap.', identity_preserved: 'I compared recognizable identity with approved references.', reference_compared: 'I compared the actual pixels with the named reference.' };
  const makeLimb = (id, person, side) => ({ id, person, side, type: 'arm', surface: 'dorsal', points: {}, occluded: {} });
  let review = { version: 1, candidate: { name: '', sha256: '' }, reference: { description: '', source: '' }, limbs: [makeLimb('person-1-limb', 'Person 1', 'unknown'), makeLimb('person-2-limb', 'Person 2', 'unknown')], contacts: [{ from: 'person-2-limb', to: 'person-1-limb', target: 'forearm', description: '' }, { from: 'person-1-limb', to: 'person-2-limb', target: 'forearm', description: '' }], checks: Object.fromEntries(Object.keys(checkLabels).map(k => [k, false])), reviewer: '', decision: 'pending', ownerApproval: { status: 'pending', evidence: '' } };
  let selectedLimb = 0, selectedPoint = 'shoulder', loadedHash = '', rejectedHashes = [], references = [];
  const limb = () => review.limbs[selectedLimb];
  function mergeRejections(input) {
    const list = Array.isArray(input) ? input : input && (input.rejectedHashes || input.rejections);
    if (!Array.isArray(list)) throw new Error('Expected a rejection array or rejectedHashes array.');
    for (const item of list) {
      const hash = (typeof item === 'string' ? item : item && item.sha256);
      if (typeof hash !== 'string' || !/^[a-f0-9]{64}$/i.test(hash)) throw new Error('Every rejection must include a valid SHA-256.');
    }
    const seen = new Set(rejectedHashes.map(item => (typeof item === 'string' ? item : item.sha256).toLowerCase()));
    list.forEach(item => { const hash = (typeof item === 'string' ? item : item.sha256).toLowerCase(); if (!seen.has(hash)) { rejectedHashes.push(typeof item === 'string' ? hash : { ...item, sha256: hash }); seen.add(hash); } });
    $('ledgerStatus').textContent = 'Rejection ledger: ' + rejectedHashes.length + ' exact image hashes loaded. Save the ledger to preserve new entries.';
  }
  function rejectCurrent() { if (review.candidate.sha256) mergeRejections([{ sha256: review.candidate.sha256, source: review.candidate.name, status: 'rejected', reason: 'Rejected in the anatomy review workbench.', reviewer: review.reviewer }]); }
  const safeText = value => typeof value === 'string' ? value : '';
  function message(text) { $('fileStatus').textContent = text; }
  function validate() {
    let result;
    try { result = window.AnatomyReviewCore ? window.AnatomyReviewCore.validate(review, rejectedHashes) : { errors: ['The annotation-checking module is unavailable. You can save a draft, but this record has not been checked.'], warnings: [], status: 'blocked' }; }
    catch (error) { result = { errors: ['The review record could not be checked: ' + error.message], warnings: [], status: 'blocked' }; }
    if (!loadedHash || loadedHash !== review.candidate.sha256) { result = { ...result, errors: [...result.errors, 'Open the candidate image matching this record before continuing the visual review.'], status: 'blocked' }; }
    $('validationStatus').textContent = result.status === 'ready_for_visual_review' ? 'Record checks passed — visual anatomy judgment still required' : 'Draft blocked — review the items below';
    $('validationMessages').replaceChildren();
    [...result.errors.map(x => 'Required: ' + x), ...result.warnings.map(x => 'Note: ' + x)].forEach(text => { const li = document.createElement('li'); li.textContent = text; $('validationMessages').append(li); });
    $('ownerStatus').textContent = 'Owner approval: ' + safeText(review.ownerApproval.status) + '. This workbench does not grant approval.';
  }
  function draw() {
    const svg = $('overlay'); svg.replaceChildren();
    const colors = ['#ffd57b', '#8ee7f0', '#faa6d2', '#b4eca0'];
    review.limbs.forEach((item, index) => {
      const color = colors[index % colors.length];
      const chain = item.type === 'leg' ? ['hip', 'knee', 'ankle'] : ['shoulder', 'elbow', 'wrist'];
      for (let i = 0; i < chain.length - 1; i++) {
        const a = item.points[chain[i]], b = item.points[chain[i + 1]];
        if (a && b) { const line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline'); line.setAttribute('points', `${a.x * 1000},${a.y * 1000} ${b.x * 1000},${b.y * 1000}`); line.setAttribute('stroke', color); svg.append(line); }
      }
      Object.entries(item.points).forEach(([key, point]) => {
        if (!point || !Number.isFinite(point.x) || !Number.isFinite(point.y)) return;
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle'); circle.setAttribute('cx', point.x * 1000); circle.setAttribute('cy', point.y * 1000); circle.setAttribute('r', index === selectedLimb && key === selectedPoint ? 10 : 7); circle.setAttribute('fill', color); svg.append(circle);
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text'); text.setAttribute('x', Math.min(point.x * 1000 + 12, 820)); text.setAttribute('y', Math.max(point.y * 1000 - 12, 22)); text.textContent = `${item.person} ${labels[key] || key}`; svg.append(text);
      });
    });
  }
  function renderLimb() {
    const current = limb();
    if (!currentPoints().includes(selectedPoint)) selectedPoint = currentPoints()[0];
    $('limbType').value = current.type || 'arm'; $('surfaceLabel').hidden = current.type === 'leg';
    $('person').value = current.person; $('side').value = current.side; $('surface').value = current.surface;
    $('occlusionReason').value = current.occluded[selectedPoint] || '';
    $('pointX').value = current.points[selectedPoint]?.x ?? ''; $('pointY').value = current.points[selectedPoint]?.y ?? '';
    $('pointButtons').replaceChildren();
    currentPoints().forEach(key => { const button = document.createElement('button'); button.type = 'button'; button.textContent = labels[key] + (current.points[key] ? ' · marked' : current.occluded[key] ? ' · hidden' : ''); button.setAttribute('aria-pressed', String(selectedPoint === key)); button.onclick = () => { selectedPoint = key; renderLimb(); }; $('pointButtons').append(button); });
    $('annotationHint').textContent = `Place ${current.person || 'this person'}’s ${current.side} ${labels[selectedPoint].toLowerCase()} on the candidate. Zoom and scroll to inspect; clicks place the selected point.`;
    draw(); validate();
  }
  function limbOptions(select, value) { select.replaceChildren(); review.limbs.forEach(item => { const option = document.createElement('option'); option.value = item.id; option.textContent = `${item.person} · ${item.side} (${item.id})`; select.append(option); }); select.value = value; }
  function renderContacts() {
    $('contacts').replaceChildren();
    review.contacts.forEach((contact, index) => {
      const box = document.createElement('div'); box.className = 'contact';
      [['from', 'Hand / limb making contact'], ['to', 'Other person’s limb'], ['target', 'Part being touched'], ['description', 'What is held and what overlaps?']].forEach(([key, title]) => {
        const label = document.createElement('label'); label.textContent = title;
        const input = document.createElement(key === 'from' || key === 'to' ? 'select' : key === 'description' ? 'textarea' : 'input');
        if (key === 'from' || key === 'to') limbOptions(input, contact[key]); else input.value = contact[key] || '';
        input.addEventListener('input', () => { contact[key] = input.value; validate(); }); label.append(input); box.append(label);
      });
      const remove = document.createElement('button'); remove.className = 'secondary'; remove.textContent = 'Remove contact'; remove.onclick = () => { review.contacts.splice(index, 1); renderContacts(); validate(); }; box.append(remove); $('contacts').append(box);
    });
  }
  function render() {
    limbOptions($('limbSelect'), limb().id); renderLimb(); renderContacts();
    $('referenceDescription').value = review.reference.description; $('referenceSource').value = review.reference.source; $('reviewer').value = review.reviewer; $('decision').value = review.decision;
    Object.keys(checkLabels).forEach(key => { $('check-' + key).checked = Boolean(review.checks[key]); }); validate();
  }
  Object.entries(checkLabels).forEach(([key, title]) => { const label = document.createElement('label'); label.className = 'check'; const input = document.createElement('input'); input.type = 'checkbox'; input.id = 'check-' + key; input.onchange = () => { review.checks[key] = input.checked; validate(); }; label.append(input, document.createTextNode(title)); $('checklist').append(label); });
  $('limbSelect').onchange = event => { selectedLimb = review.limbs.findIndex(x => x.id === event.target.value); renderLimb(); };
  ['person', 'side', 'surface'].forEach(key => { $(key).oninput = () => { limb()[key] = $(key).value; limbOptions($('limbSelect'), limb().id); renderContacts(); draw(); validate(); }; });
  $('limbType').onchange = () => { limb().type = $('limbType').value; limb().points = {}; limb().occluded = {}; Object.keys(review.checks).forEach(key => { review.checks[key] = false; }); message('Limb type changed. Its landmarks and review checks were reset.'); render(); };
  $('addLimb').onclick = () => { const id = 'limb-' + Date.now().toString(36); review.limbs.push(makeLimb(id, 'Person ' + (review.limbs.length + 1), 'unknown')); selectedLimb = review.limbs.length - 1; render(); };
  $('addContact').onclick = () => { review.contacts.push({ from: limb().id, to: review.limbs.find(x => x.id !== limb().id)?.id || limb().id, target: '', description: '' }); renderContacts(); validate(); };
  $('overlay').onclick = event => { if (!loadedHash || loadedHash !== review.candidate.sha256) return; const rect = $('overlay').getBoundingClientRect(); if (!rect.width || !rect.height) return; limb().points[selectedPoint] = { x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)), y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)) }; delete limb().occluded[selectedPoint]; renderLimb(); };
  $('placePoint').onclick = () => { if (!loadedHash || loadedHash !== review.candidate.sha256) { message('Open the matching candidate before placing a landmark.'); return; } const xText = $('pointX').value.trim(), yText = $('pointY').value.trim(), x = Number(xText), y = Number(yText); if (!xText || !yText || !Number.isFinite(x) || !Number.isFinite(y) || x < 0 || x > 1 || y < 0 || y > 1) { message('Enter both coordinates as numbers between 0 and 1.'); return; } limb().points[selectedPoint] = { x, y }; delete limb().occluded[selectedPoint]; renderLimb(); message('Selected landmark placed. Inspect its location in the image.'); };
  $('resetPoint').onclick = () => { delete limb().points[selectedPoint]; delete limb().occluded[selectedPoint]; renderLimb(); };
  $('markOccluded').onclick = () => { const reason = $('occlusionReason').value.trim(); if (!reason) { message('Describe why the selected landmark is hidden.'); $('occlusionReason').focus(); return; } delete limb().points[selectedPoint]; limb().occluded[selectedPoint] = reason; renderLimb(); };
  $('zoom').onchange = () => { $('candidateCanvas').style.width = (Number($('zoom').value) * 100) + '%'; };
  function readFile(file, method) { return new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result); reader.onerror = () => reject(new Error('The selected file could not be read.')); reader[method](file); }); }
  $('candidateFile').onchange = async event => {
    const file = event.target.files[0]; if (!file) return;
    try { const buffer = await readFile(file, 'readAsArrayBuffer'); const digest = await crypto.subtle.digest('SHA-256', buffer); const hash = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
      if (review.candidate.sha256 && review.candidate.sha256 !== hash) { review.limbs.forEach(item => { item.points = {}; item.occluded = {}; }); Object.keys(review.checks).forEach(key => { review.checks[key] = false; }); review.decision = 'pending'; review.ownerApproval = { status: 'pending', evidence: '' }; message('Different candidate opened. Landmark positions, checks, and approval were reset.'); } else message(file.name + ' · SHA-256 ' + hash.slice(0, 12) + '…');
      review.candidate = { name: file.name, sha256: hash }; loadedHash = hash; $('candidateImage').src = await readFile(file, 'readAsDataURL'); $('candidateImage').hidden = false; $('emptyImage').hidden = true; $('zoom').value = '1'; $('candidateCanvas').style.width = '100%'; render();
    } catch (error) { message(error.message + ' Use a local server if your browser does not support file hashing here.'); }
  };
  function refreshReferences() { const select = $('referenceSelect'); select.replaceChildren(); references.forEach((ref, i) => { const option = document.createElement('option'); option.value = i; option.textContent = ref.name || ref.description || 'Reference ' + (i + 1); select.append(option); }); if (references.length) { select.value = String(references.length - 1); showReference(); } }
  function showReference() { const ref = references[Number($('referenceSelect').value)]; if (!ref) return; $('referenceImage').src = ref.url; $('referenceImage').hidden = false; $('referenceSources').replaceChildren(); if (ref.source) { const p = document.createElement('p'); p.className = 'hint'; if (/^https?:\/\//i.test(ref.source)) { const a = document.createElement('a'); a.href = ref.source; a.textContent = ref.source; a.target = '_blank'; a.rel = 'noopener noreferrer'; p.append(a); } else p.textContent = ref.source; $('referenceSources').append(p); } }
  $('referenceSelect').onchange = showReference;
  $('referenceFiles').onchange = async event => { try { for (const file of event.target.files) references.push({ name: file.name, url: await readFile(file, 'readAsDataURL'), source: 'Local reference: ' + file.name }); refreshReferences(); } catch (error) { message(error.message); } };
  $('referenceDescription').oninput = () => { review.reference.description = $('referenceDescription').value; validate(); };
  $('referenceSource').oninput = () => { review.reference.source = $('referenceSource').value; validate(); };
  $('reviewer').oninput = () => { review.reviewer = $('reviewer').value; validate(); };
  $('decision').onchange = () => { review.decision = $('decision').value; if (review.decision === 'rejected') rejectCurrent(); validate(); };
  $('reject').onclick = () => { review.decision = 'rejected'; rejectCurrent(); $('decision').value = 'rejected'; validate(); message('Candidate marked rejected in this review. Save the JSON to preserve the record.'); };
  $('saveReview').onclick = () => { const blob = new Blob([JSON.stringify(review, null, 2) + '\n'], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = (review.candidate.name || 'anatomy-review').replace(/\.[^.]+$/, '') + '-review.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); message('Review JSON saved as a record, including any incomplete checks.'); };
  function normalizeImport(data) {
    const object = x => !!x && typeof x === 'object' && !Array.isArray(x);
    const fail = () => { throw new Error('Malformed review: candidate, limbs, landmarks, occlusions, and contacts must follow the version 1 format.'); };
    if (!object(data) || data.version !== 1 || !object(data.candidate) || typeof data.candidate.name !== 'string' || typeof data.candidate.sha256 !== 'string' || (data.candidate.sha256 && !/^[a-f0-9]{64}$/i.test(data.candidate.sha256)) || !Array.isArray(data.limbs) || !data.limbs.length || !Array.isArray(data.contacts)) fail();
    const ids = new Set();
    data.limbs.forEach(item => {
      if (!object(item) || typeof item.id !== 'string' || !item.id.trim() || ids.has(item.id) || typeof item.person !== 'string' || !['left','right','unknown'].includes(item.side) || !['arm','leg',undefined].includes(item.type) || typeof item.surface !== 'string' || !object(item.points) || !object(item.occluded)) fail();
      ids.add(item.id);
      const names = pointSets[item.type || 'arm'];
      Object.entries(item.points).forEach(([key, p]) => { if (!names.includes(key) || !object(p) || !Number.isFinite(p.x) || !Number.isFinite(p.y) || p.x < 0 || p.x > 1 || p.y < 0 || p.y > 1) fail(); });
      Object.entries(item.occluded).forEach(([key, value]) => { if (!names.includes(key) || typeof value !== 'string') fail(); });
    });
    data.contacts.forEach(item => { if (!object(item) || !['from','to','target','description'].every(key => typeof item[key] === 'string') || !ids.has(item.from) || !ids.has(item.to)) fail(); });
    if (data.reference !== undefined && (!object(data.reference) || !['description','source'].every(key => typeof data.reference[key] === 'string'))) fail();
    if (data.checks !== undefined && (!object(data.checks) || Object.values(data.checks).some(value => typeof value !== 'boolean'))) fail();
    if (data.ownerApproval !== undefined && (!object(data.ownerApproval) || typeof data.ownerApproval.status !== 'string' || typeof data.ownerApproval.evidence !== 'string')) fail();
    return { ...data, candidate: { name: data.candidate.name, sha256: data.candidate.sha256.toLowerCase() }, reference: { description: '', source: '', ...data.reference }, checks: { ...Object.fromEntries(Object.keys(checkLabels).map(k => [k, false])), ...data.checks }, reviewer: safeText(data.reviewer), decision: safeText(data.decision) || 'pending', ownerApproval: { status: 'pending', evidence: '', ...data.ownerApproval } };
  }
  $('reviewFile').onchange = async event => {
    const file = event.target.files[0]; if (!file) return;
    try {
      const next = normalizeImport(JSON.parse(await readFile(file, 'readAsText')));
      review = next; selectedLimb = 0;
      if (review.decision === 'rejected') rejectCurrent();
      if (loadedHash !== review.candidate.sha256) { loadedHash = ''; $('candidateImage').removeAttribute('src'); $('candidateImage').hidden = true; $('emptyImage').hidden = false; }
      render(); message('Review restored. ' + (loadedHash ? 'Candidate hash matches the open image.' : 'Open the matching candidate image to inspect its annotations.'));
    } catch (error) { message('Could not load review: ' + error.message); }
  };
  $('ledgerFile').onchange = async event => { const file = event.target.files[0]; if (!file) return; try { mergeRejections(JSON.parse(await readFile(file, 'readAsText'))); validate(); message('Rejection ledger imported and merged.'); } catch (error) { message('Could not import ledger: ' + error.message); } };
  $('saveLedger').onclick = () => { const url = URL.createObjectURL(new Blob([JSON.stringify(rejectedHashes, null, 2) + '\n'], { type: 'application/json' })); const a = document.createElement('a'); a.href = url; a.download = 'rejected-hashes.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); message('Rejection ledger saved. Keep it with your next private review workbench.'); };
  fetch('rejected-hashes.json').then(response => { if (!response.ok) throw new Error('No default ledger found.'); return response.json(); }).then(data => { mergeRejections(data); validate(); }).catch(() => { if (rejectedHashes.length) return; $('ledgerStatus').textContent = 'No default rejection ledger loaded. Import your saved ledger before reviewing candidates.'; });
  // Optional private manifest. Only local image paths are accepted; no remote images are fetched.
  fetch('references.json').then(response => response.ok ? response.json() : null).then(data => { if (!data) return; if (Array.isArray(data.rejectedHashes)) mergeRejections(data.rejectedHashes); const list = Array.isArray(data) ? data : data.references; if (!Array.isArray(list)) return; list.forEach(ref => { const path = ref.path || ref.file; if (typeof path !== 'string' || /^(?:[a-z]+:|\/\/)/i.test(path)) return; references.push({ name: ref.name || ref.title, description: ref.description, source: ref.source || '', url: path }); }); refreshReferences(); validate(); }).catch(() => {});
  render();
})();
