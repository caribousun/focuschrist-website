'use strict';
/* Exact event/target manifest: mechanical binding, not editorial approval. */
const crypto=require('node:crypto');
const SHA='239a9200fd3c8deaff47663d0d35f469df2abfe6bfedcabbbe65bbd839fbd992';
function read(raw){
 if(crypto.createHash('sha256').update(raw).digest('hex')!==SHA)throw new Error('Unreviewed event destination bindings');
 const rows=JSON.parse(raw);if(!Array.isArray(rows)||rows.length!==51||new Set(rows.map(r=>r.timeline+':'+r.index)).size!==51)throw new Error('Invalid event binding coverage');
 const active=rows.filter(r=>r.target);if(active.length!==50||new Set(active.map(r=>r.target)).size!==50)throw new Error('Invalid event target coverage');
 const pending=rows.filter(r=>!r.target);if(pending.length!==1||pending[0].timeline!=='handcart'||pending[0].index!==28||pending[0].event!=='The Needles')throw new Error('Unexpected unresolved event');
 return rows;
}
module.exports={read,SHA};
