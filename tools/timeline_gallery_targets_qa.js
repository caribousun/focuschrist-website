/* Exact gallery deep links used by the timeline, including a missing-record negative. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const catalog=JSON.parse(read('art-gallery.json'));
const ids=['art-4f5759d8edad','art-838305f993f7','art-3b1016debbad','art-6e45c602be15','art-d12945c2d847'];
async function check(id,missing){
 const dom=new JSDOM(read('art-gallery.html'),{url:'https://focuschrist.com/art-gallery.html?picture='+id,runScripts:'outside-only'}),w=dom.window;
 const art=catalog.artworks.find(x=>x.id===id);assert(art&&art.occurrences.length);
 w.fetch=async()=>({ok:true,json:async()=>({...catalog,artworks:missing?catalog.artworks.filter(x=>x.id!==id):catalog.artworks})});
 w.eval(read('art-gallery.js'));await new Promise(resolve=>setImmediate(resolve));
 const frame=w.document.getElementById('artGalleryFrame');
 if(missing){assert(w.document.getElementById('artGalleryCount').textContent.includes('no longer in the gallery'));assert(!frame.src||frame.src==='about:blank');}
 else{const u=new URL(frame.src);assert.equal(u.pathname,art.occurrences[0].page);assert.equal(u.searchParams.get('gallery-art'),art.occurrences[0].id);}
 w.close();
}
(async()=>{for(const id of ids)await check(id,false);await check(ids[0],true);console.log('PASS: five exact timeline artwork links open their owning gallery records; missing target rejected.');})().catch(e=>{console.error(e);process.exitCode=1});
