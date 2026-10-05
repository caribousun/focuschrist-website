const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const file=require('path').join(__dirname,'..','timeline-terrain.js');
const source=fs.readFileSync(file,'utf8'),results=[];
function fixture(){
 const cb={},events=[],state={loaded:true,sources:{'terrain-dem':true,openmaptiles:true,ne2_shaded:true}};
 const gl={on:(n,f)=>cb[n]=f,loaded:()=>state.loaded,isSourceLoaded:id=>state.sources[id]===true};
 const adapter={maplibreGL:()=>({addTo(){},getMaplibreMap:()=>gl})};
 const ctx={URL,document:{currentScript:{src:'https://focuschrist.com/timeline-terrain.js'}},window:{maplibregl:{},MaplibreGLLeaflet:adapter},MaplibreGLLeaflet:adapter};
 vm.runInNewContext(source,ctx);ctx.window.FCTerrainLayer().on('tileload',()=>events.push('load')).on('tileerror',()=>events.push('error')).addTo({attributionControl:{addAttribution(){}}});
 return {cb,events,state,content:(id='terrain-dem')=>cb.sourcedata({sourceId:id,sourceDataType:'content'}),error:id=>cb.error({sourceId:id,error:Error('fixture failure')}),idle:()=>cb.idle(),loads:()=>events.filter(v=>v==='load').length};
}
function test(name,fn){try{fn();results.push({name,pass:true})}catch(e){results.push({name,pass:false,message:e.message})}}
test('DEM optional tile absent succeeds after settle',()=>{let t=fixture();t.content();t.idle();assert.equal(t.loads(),1)});
test('DEM metadata alone cannot establish readiness',()=>{let t=fixture();t.cb.sourcedata({sourceId:'terrain-dem',sourceDataType:'metadata'});t.idle();assert.equal(t.loads(),0)});
test('vector failure cannot recover with DEM success alone',()=>{let t=fixture();t.error('openmaptiles');t.content();t.idle();assert.equal(t.loads(),0)});
test('vector metadata cannot recover failed vector',()=>{let t=fixture();t.error('openmaptiles');t.content();t.cb.sourcedata({sourceId:'openmaptiles',sourceDataType:'metadata'});t.idle();assert.equal(t.loads(),0)});
test('failed vector content cannot recover while vector unsettled',()=>{let t=fixture();t.error('openmaptiles');t.content();t.state.sources.openmaptiles=false;t.content('openmaptiles');t.idle();assert.equal(t.loads(),0)});
test('all implicated sources must recover',()=>{let t=fixture();t.error('openmaptiles');t.error('terrain-dem');t.content();t.idle();assert.equal(t.loads(),0);t.content('openmaptiles');t.idle();assert.equal(t.loads(),1)});
test('late vector failure hides readiness until vector and DEM success',()=>{let t=fixture();t.content();t.idle();t.error('openmaptiles');t.content();t.idle();assert.equal(t.loads(),1);t.content('openmaptiles');t.idle();assert.equal(t.loads(),2)});
test('a repeated failure cancels earlier source success',()=>{let t=fixture();t.error('openmaptiles');t.content('openmaptiles');t.error('openmaptiles');t.content();t.idle();assert.equal(t.loads(),0)});
test('unidentified error cannot recover from arbitrary DEM content',()=>{let t=fixture();t.error(undefined);t.content();t.content('openmaptiles');t.idle();assert.equal(t.loads(),0)});
test('global loaded false blocks ready even with source success',()=>{let t=fixture();t.content();t.state.loaded=false;t.idle();assert.equal(t.loads(),0)});
const report={file,sha256:crypto.createHash('sha256').update(source).digest('hex'),results,pass:results.every(x=>x.pass),limits:'Independent VM event contract; no claim of rendered pixels, network completeness, or WebGL recovery.'};
console.log(JSON.stringify(report,null,2));if(!report.pass)process.exitCode=1;

const root=require('path').join(__dirname,'..');
const mobile=fs.readFileSync(require('path').join(root,'timeline-mobile-study.css'),'utf8');
assert(mobile.includes('.timeline-mobile .timeline-map-unavailable #map:has(>.leaflet-container):has(>.map-fallback){height:240px!important;min-height:240px!important}'),'Handcart fallback must retain a readable map area');
assert(fs.readFileSync(require('path').join(root,'timelines/willie-and-martin-handcart-map.html'),'utf8').includes("fallback.setAttribute('tabindex','0')"),'Overflow fallback must be keyboard focusable');
