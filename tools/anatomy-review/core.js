(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.AnatomyReviewCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const POINTS = ['shoulder', 'elbow', 'wrist', 'index_mcp', 'little_mcp', 'thumb_base'];
  const POINTS_BY_TYPE = {arm: POINTS, leg: ['hip', 'knee', 'ankle', 'heel', 'big_toe', 'little_toe']};
  const CHECKS = ['whole_chain', 'hand_ownership', 'digits_and_thumb', 'contact_and_overlap', 'identity_preserved', 'reference_compared'];
  const validPoint = p => !!p && Number.isFinite(p.x) && Number.isFinite(p.y) && p.x >= 0 && p.x <= 1 && p.y >= 0 && p.y <= 1;
  const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  const nonempty = value => typeof value === 'string' && value.trim().length > 0;

  function validate(review, rejectedHashes = []) {
    const errors = [], warnings = [];
    const r = review || {};
    if (r.version !== 1) errors.push('Unsupported or missing review version.');
    const hash = r.candidate && r.candidate.sha256;
    if (!/^[a-f0-9]{64}$/i.test(hash || '')) errors.push('Load a candidate and record its exact SHA-256.');
    if (Array.isArray(rejectedHashes) && rejectedHashes.some(item => String(typeof item === 'string' ? item : item?.sha256 || '').toLowerCase() === String(hash || '').toLowerCase())) errors.push('These exact image bytes were rejected. A new filename does not clear a rejection.');
    if (r.decision === 'rejected') errors.push('The reviewer marked this candidate rejected.');
    if (!nonempty(r.reviewer)) errors.push('Name the person who inspected the actual image.');
    if (!r.reference || !nonempty(r.reference.description) || !nonempty(r.reference.source)) errors.push('Record the pose reference and its source.');
    const limbs = Array.isArray(r.limbs) ? r.limbs : [];
    if (!limbs.length) errors.push('Map at least one complete limb.');
    const ids = new Set();
    for (const limb of limbs) {
      if (!limb || typeof limb !== 'object') { errors.push('Each limb must be an annotation object.'); continue; }
      const label = limb.id || 'Unnamed limb';
      if (!nonempty(limb.id) || ids.has(limb.id)) errors.push(label + ': limb identifiers must be unique.');
      ids.add(limb.id);
      if (!nonempty(limb.person)) errors.push(label + ': identify whose limb this is.');
      if (!['left', 'right'].includes(limb.side)) errors.push(label + ': specify the person’s anatomical left or right, not screen side.');
      const type = limb.type || 'arm';
      if (!POINTS_BY_TYPE[type]) errors.push(label + ': unsupported limb type.');
      if (type === 'arm' && !['palmar', 'dorsal', 'edge', 'oblique'].includes(limb.surface)) errors.push(label + ': identify the visible hand surface.');
      const p = limb.points || {}, occluded = limb.occluded || {};
      for (const key of POINTS_BY_TYPE[type] || POINTS) {
        if (p[key] && nonempty(occluded[key])) errors.push(label + ': ' + key + ' cannot be both located and occluded.');
        else if (p[key] && !validPoint(p[key])) errors.push(label + ': ' + key + ' must lie within the image.');
        else if (!p[key] && !nonempty(occluded[key])) errors.push(label + ': locate ' + key + ' or explain its occlusion.');
        else if (!p[key]) warnings.push(label + ': ' + key + ' is occluded; confirm continuity against the complete pose reference.');
      }
      if (type === 'leg' && ['hip', 'knee', 'ankle'].every(k => validPoint(p[k]))) {
        if (distance(p.hip, p.knee) < 0.002 || distance(p.knee, p.ankle) < 0.002) errors.push(label + ': distinct leg joints occupy the same point.');
      }
      if (['shoulder', 'elbow', 'wrist'].every(k => validPoint(p[k]))) {
        const upper = distance(p.shoulder, p.elbow), lower = distance(p.elbow, p.wrist);
        if (upper < 0.002 || lower < 0.002) errors.push(label + ': distinct joints occupy the same point; the chain is not traced.');
        else if (upper / lower < 0.25 || upper / lower > 4) warnings.push(label + ': large projected limb-length difference; inspect foreshortening rather than treating a 2D ratio as anatomy proof.');
      }
      if (['index_mcp', 'little_mcp', 'thumb_base'].every(k => validPoint(p[k]))) {
        const index = p.index_mcp, little = p.little_mcp, thumb = p.thumb_base;
        const vx = index.x - little.x, vy = index.y - little.y, length2 = vx * vx + vy * vy;
        if (length2 < 0.000004) errors.push(label + ': index and little-finger knuckles are not distinct.');
        else {
          const towardIndex = ((thumb.x - (index.x + little.x) / 2) * vx + (thumb.y - (index.y + little.y) / 2) * vy) / length2;
          if (towardIndex < -0.15) errors.push(label + ': annotated thumb base lies on the little-finger side. Recheck labels, handedness and perspective before accepting.');
          if (limb.surface === 'edge' || limb.surface === 'oblique') warnings.push(label + ': an oblique/edge projection cannot establish handedness from screen position alone.');
        }
      }
    }
    for (const contact of Array.isArray(r.contacts) ? r.contacts : []) {
      if (!contact || typeof contact !== 'object') { errors.push('Each contact must be an annotation object.'); continue; }
      if (!ids.has(contact.from) || !ids.has(contact.to)) errors.push('Contact refers to a limb that has not been mapped.');
      if (contact.from === contact.to) errors.push('An assisting grasp must not be assigned to the same limb at both ends.');
      if (!nonempty(contact.target) || !nonempty(contact.description)) errors.push('Describe what each hand contacts and how its fingers wrap.');
    }
    for (const key of CHECKS) if (!r.checks || r.checks[key] !== true) errors.push('Actual-image inspection incomplete: ' + key.replace(/_/g, ' ') + '.');
    if (r.ownerApproval && r.ownerApproval.status === 'approved' && !nonempty(r.ownerApproval.evidence)) errors.push('Owner approval requires the owner’s explicit evidence; a technical review cannot supply it.');
    warnings.push('This tool checks review completeness and annotation consistency. It cannot certify the anatomy, realism, joint safety or load-bearing ability of generated pixels.');
    return { errors, warnings, status: errors.length ? 'blocked' : 'ready_for_visual_review' };
  }

  function buildPrompt(review) {
    const limbs = (review.limbs || []).filter(l => l && typeof l === 'object').map(l => l.type === 'leg'
      ? l.person + ': anatomical ' + l.side + ' leg. Trace hip → knee → lower leg → ankle → heel and foot, identifying the big-toe and little-toe sides.'
      : l.person + ': anatomical ' + l.side + ' arm; visible surface ' + l.surface + '. Trace shoulder → elbow → forearm → wrist → hand.');
    const contacts = (review.contacts || []).filter(c => c && typeof c === 'object').map(c => c.from + ' contacts ' + c.to + ' at ' + c.target + ': ' + c.description);
    return ['Use the supplied complete-pose reference; do not infer left/right from screen side.', ...limbs, ...contacts,
      'Keep each limb separately traceable throughout overlap. Every finger belongs to one hand and wrist; every foot belongs to one ankle and leg. Do not infer occluded anatomy from completed annotations.',
      'Preserve actual approved identity references and scene-specific expression. Rebuild the connected limb pose after repeated failed local edits.',
      'After generation, inspect full-body continuity, close hands, contact and phone rendering. Do not call generation or a completed checklist owner approval.'].join('\n');
  }
  return { POINTS, POINTS_BY_TYPE, CHECKS, validate, buildPrompt };
});
