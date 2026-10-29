/* Offline review aid. It never edits reports, contacts providers, or grants release approval. */
'use strict';
function assess(row){
 const outcome={originalStatus:typeof row?.status==='string'?row.status:null,classification:'UNRESOLVED',matchedCancellation:null,scope:'Correlation only; neither cancellation cause nor complete visible-tile success is proven. Independent pixel review and release checks remain separate.'};
 if(!row||row.status!=='FAIL'||row.denied!==false||row.denial!==null||row.error||row.failedRequests!==1)return outcome;
 const zeros=['pageErrors','badResponses','blockedRequests','blockedRedirects','boundaryErrors','handlerErrors','eventsDropped','sourceTraceDropped','sourceErrors','mapEventsDropped'];
 if(zeros.some(k=>row[k]!==0)||row.handlerDrainTimeout!==false||row.sourceObserverAttached!==true||row.sourceObservationComplete!==true)return outcome;
 if(!['sourcesLoaded','rendererLoaded','statusHidden','canvasVisible'].every(k=>row[k]===true)||!(row.openfreemapResponses>0&&row.mapterhornResponses>0))return outcome;
 if(!row.finalSourceLoaded||!['ne2_shaded','openmaptiles','terrain-dem'].every(k=>row.finalSourceLoaded[k]===true))return outcome;
 if(!Number.isSafeInteger(row.sourceObservationCutoffEpochMs)||!Array.isArray(row.events)||!Array.isArray(row.sourceEvents)||!Array.isArray(row.requestErrors)||!Array.isArray(row.responseErrors)||row.responseErrors.length)return outcome;
 const record=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
 if(!row.events.every(e=>record(e)&&typeof e.kind==='string')||!row.sourceEvents.every(e=>record(e)&&['sourcedataabort','error'].includes(e.type))||!row.requestErrors.every(record))return outcome;
 if(row.events.some(e=>e.kind==='route-error'))return outcome;
 if(row.requestErrors.length!==1||row.requestErrors[0].host!=='tiles.openfreemap.org'||row.requestErrors[0].code!=='net::ERR_ABORTED')return outcome;
 const failed=row.events.filter(e=>e.kind==='request-failed');
 if(failed.length!==1)return outcome;
 const f=failed[0],tile=f.tile;
 if(!Number.isSafeInteger(f.id)||f.id<1||f.code!=='net::ERR_ABORTED'||f.host!=='tiles.openfreemap.org'||f.path!=='/natural_earth/ne2sr/{z}/{x}/{y}.png'||!tile||tile.source!=='ne2_shaded')return outcome;
 if(!Number.isInteger(tile.z)||tile.z<0||tile.z>22||!Number.isInteger(tile.x)||tile.x<0||tile.x>=2**tile.z||!Number.isInteger(tile.y)||tile.y<0||tile.y>=2**tile.z)return outcome;
 const sameTile=t=>t&&t.source===tile.source&&t.z===tile.z&&t.x===tile.x&&t.y===tile.y;
 const matchingRequests=row.events.filter(e=>e.kind==='request'&&e.host===f.host&&e.path===f.path&&sameTile(e.tile));
 if(matchingRequests.length!==1||matchingRequests[0].id!==f.id)return outcome;
 const eventsForId=row.events.filter(e=>e.id===f.id);
 const one=kind=>{const a=eventsForId.filter(e=>e.kind===kind);return a.length===1?a[0]:null;};
 const start=one('request'),fetch=one('route-fetch-start'),response=one('route-fetch-response'),fulfilled=one('route-fulfilled');
 if(!start||!fetch||!response||!fulfilled||response.status!==200||fulfilled.status!==200||eventsForId.some(e=>e.kind==='route-error'||e.kind==='request-finished'))return outcome;
 if(eventsForId.some(e=>e.host!==f.host||e.path!==f.path||!sameTile(e.tile)||!Number.isSafeInteger(e.epochMs)))return outcome;
 const aborts=row.sourceEvents.filter(e=>e.type==='sourcedataabort');
 const validAbort=e=>{const c=e.coord;return ['ne2_shaded','openmaptiles','terrain-dem'].includes(e.source)&&c&&Number.isInteger(c.z)&&c.z>=0&&c.z<=22&&Number.isInteger(c.x)&&c.x>=0&&c.x<2**c.z&&Number.isInteger(c.y)&&c.y>=0&&c.y<2**c.z&&Number.isSafeInteger(e.epochMs)&&e.epochMs<=row.sourceObservationCutoffEpochMs;};
 if(row.sourceEvents.some(e=>e.type==='error')||!aborts.every(validAbort))return outcome;
 const matches=aborts.filter(e=>e.source===tile.source&&e.coord.z===tile.z&&e.coord.x===tile.x&&e.coord.y===tile.y);
 if(matches.length!==1)return outcome;
 const abort=matches[0];
 // Clock timestamps must show this strict sequence; no cause is inferred from it.
 if(!(start.epochMs<=fetch.epochMs&&fetch.epochMs<abort.epochMs&&abort.epochMs<f.epochMs&&f.epochMs<response.epochMs&&response.epochMs<=fulfilled.epochMs&&f.epochMs<=row.sourceObservationCutoffEpochMs))return outcome;
 outcome.classification='MATCHED_RENDERER_CANCELLATION';
 outcome.matchedCancellation={requestId:f.id,source:tile.source,z:tile.z,x:tile.x,y:tile.y,requestEpochMs:start.epochMs,sourceAbortEpochMs:abort.epochMs,requestFailureEpochMs:f.epochMs,fetchResponseEpochMs:response.epochMs,fetchFulfilledEpochMs:fulfilled.epochMs};
 return outcome;
}
module.exports={assess};
