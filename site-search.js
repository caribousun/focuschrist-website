/* Published-content discovery. No query is sent to an answer provider. */
(function (root) {
    'use strict';
    const STOP = new Set('a an the is are was were do does did what how why when where who which can could would should i me my we our you your to of for in on and or about with please tell'.split(' '));
    function normalize(value) {
        return String(value || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
            .replace(/d\s*&\s*c\b/g, 'doctrine and covenants').replace(/\brestored\b/g,'restoration').replace(/[^a-z0-9]+/g, ' ').trim();
    }
    function terms(query) { return [...new Set(normalize(query).split(' ').filter(x => x && !STOP.has(x)))]; }
    function rank(records, query) {
        const words = terms(query); if (!words.length) return [];
        const phrase = normalize(query);
        return records.map(record => {
            const title=normalize(record.title), page=normalize(record.pageTitle), body=normalize(record.text), keys=normalize(record.keywords);
            const haystack=title+' '+page+' '+body+' '+keys;
            if (!words.every(word => haystack.includes(word))) return null;
            const score=words.reduce((sum, word) => sum+(title.includes(word)?30:0)+(keys.includes(word)?35:0)+(page.includes(word)?4:0),0)
                +(title===phrase?100:0)+(title.includes(phrase)?40:0)+(record.url.includes('#')?2:0);
            return {record,score};
        }).filter(Boolean).sort((a,b)=>b.score-a.score || a.record.url.localeCompare(b.record.url)).map(x=>x.record);
    }
    function excerpt(record, query) {
        const text=record.excerpt || record.text || '';
        if (text.length<=240) return text;
        const words=terms(query), lower=text.toLowerCase();
        const hits=words.map(w=>lower.indexOf(w)).filter(i=>i>=0);
        let start=hits.length?Math.max(0,Math.min(...hits)-65):0;
        if(start) { const space=text.indexOf(' ',start); if(space>=0) start=space+1; }
        let end=Math.min(text.length,start+235);
        if(end<text.length) { const space=text.lastIndexOf(' ',end); if(space>start) end=space; }
        return (start?'… ':'')+text.slice(start,end)+(end<text.length?' …':'');
    }
    function localURL(value) { return typeof value==='string' && /^\/(?!\/)[a-zA-Z0-9_./%?=&#+-]+$/.test(value) && !value.includes('..'); }
    function groupMatches(records, query) {
        const words=terms(query), best=[], supporting=[];
        rank(records,query).forEach(record=>{
            const subject=terms(record.title+' '+(record.keywords||''));
            (words.every(word=>subject.includes(word))?best:supporting).push(record);
        });
        return {best,supporting};
    }
    const api={rank,groupMatches,excerpt,normalize,terms,localURL};
    if(typeof module!=='undefined' && module.exports) module.exports=api;
    if(!root || !root.document) return;
    const doc=root.document;
    const script=doc.currentScript;
    const base=new URL('.',script ? script.src : root.location.href);
    const searchURL=new URL('search.html',base);
    function element(tag, cls, text) { const n=doc.createElement(tag); if(cls)n.className=cls; if(text)n.textContent=text; return n; }
    function form(id) {
        const f=element('form','fc-search-form'); f.action=searchURL.href; f.method='get'; f.setAttribute('role','search');
        const label=element('label','', 'Search focusChrist'); label.htmlFor=id;
        const row=element('div','fc-search-row'); const input=element('input'); input.id=id; input.name='q'; input.type='search'; input.maxLength=200; input.required=true;
        input.placeholder='Topics, questions, scripture references, and studies';
        const button=element('button','fc-button fc-button--primary','Search'); button.type='submit'; row.append(input,button); f.append(label,row); return f;
    }
    function initHeader() {
        const trigger=doc.querySelector('[data-site-search-trigger]'); if(!trigger || doc.getElementById('fc-search-dialog'))return;
        const dialog=element('dialog','fc-search-dialog'); dialog.id='fc-search-dialog'; dialog.setAttribute('aria-labelledby','fc-search-dialog-title');
        const heading=element('h2','','Find something to study'); heading.id='fc-search-dialog-title';
        const close=element('button','fc-search-close','Close'); close.type='button';
        const f=form('fc-header-search'); dialog.append(close,heading,f);doc.body.append(dialog);
        trigger.setAttribute('aria-haspopup','dialog'); trigger.setAttribute('aria-controls',dialog.id);
        trigger.addEventListener('click',event=>{
            if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
            if(typeof dialog.showModal!=='function')return;
            event.preventDefault();
            const menu=doc.getElementById('hamburgerMenu'); if(menu)menu.classList.remove('show');
            const hamburger=doc.querySelector('.hamburger'); if(hamburger)hamburger.setAttribute('aria-expanded','false');
            dialog.showModal(); f.querySelector('input').focus();
        });
        close.addEventListener('click',()=>dialog.close());
        dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
        dialog.addEventListener('close',()=>{if(!dialog.open)trigger.focus({preventScroll:true});});
    }
    function initResults() {
        const host=doc.querySelector('[data-search-results]'); if(!host)return;
        const f=doc.getElementById('fc-results-search-form'), input=f.querySelector('input');
        const status=doc.getElementById('fc-search-status'), more=doc.getElementById('fc-search-more');
        const ask=doc.getElementById('fc-search-ask'), retry=doc.getElementById('fc-search-retry');
        const bestHeading=element('h2','fc-search-group-title','Best matches');host.before(bestHeading);
        const related=element('details','fc-search-supporting');
        const summary=element('summary');
        const explanation=element('p','','These pages mention your search or offer related context. They may focus on a different topic.');
        const relatedHost=element('ol','fc-search-results');relatedHost.setAttribute('aria-label','Supporting references');
        const relatedMore=element('button','fc-button','Show more supporting references');relatedMore.type='button';
        related.append(summary,explanation,relatedHost,relatedMore);more.after(related);
        let indexPromise, matching=[], supporting=[], shown=0, relatedShown=0, sequence=0, activeQuery='';
        function getIndex(){
            if(!indexPromise) indexPromise=fetch(new URL('site-search-index.json',base),{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('Index unavailable');return r.json();}).then(data=>{
                if(data.version!==1 || !Array.isArray(data.records) || !data.records.length || data.records.some(r=>!localURL(r.url)||typeof r.title!=='string'||typeof r.text!=='string'))throw Error('Invalid index');
                return data.records;
            }).catch(e=>{indexPromise=null;throw e;});
            return indexPromise;
        }
        function appendResults(query, isSupporting=false){
            const list=isSupporting?supporting:matching, target=isSupporting?relatedHost:host, start=isSupporting?relatedShown:shown;
            list.slice(start,start+12).forEach(r=>{
                const item=element('li','fc-search-result');
                if(r.thumbnail && localURL(r.thumbnail)){const imageLink=element('a');imageLink.href=r.url;imageLink.tabIndex=-1;imageLink.setAttribute('aria-hidden','true');const img=element('img');img.src=new URL(r.thumbnail,root.location.origin).href;img.alt='';img.loading='lazy';img.width=112;img.height=84; imageLink.append(img);item.append(imageLink);}
                const copy=element('div','fc-search-result-copy');copy.append(element('p','fc-search-category',r.category+' · '+r.pageTitle));
                const heading=element('h2');const link=element('a','',r.title);link.href=r.url;heading.append(link);copy.append(heading,element('p','fc-search-excerpt',excerpt(r,query)));item.append(copy);target.append(item);
            });
            if(isSupporting){relatedShown=Math.min(start+12,list.length);relatedMore.hidden=relatedShown>=list.length;}
            else {shown=Math.min(start+12,list.length);more.hidden=shown>=list.length;}
            status.textContent=matching.length?matching.length+' best '+(matching.length===1?'match':'matches')+' for “'+query+'”'+(matching.length>shown?' · Showing '+shown:'')+(supporting.length?' · '+supporting.length+' supporting references below':''):'No direct topic matches for “'+query+'”. Supporting references may help you explore further.';
        }
        async function run(){
            const current=++sequence;
            const query=(new URL(root.location.href).searchParams.get('q')||'').trim().slice(0,200); input.value=query;activeQuery=query;
            host.replaceChildren();relatedHost.replaceChildren();more.hidden=true;retry.hidden=true;related.hidden=true;related.open=false;bestHeading.hidden=true;matching=[];supporting=[];shown=0;relatedShown=0;
            const askURL=new URL('ask.html',base); if(query)askURL.searchParams.set('search-question',query);askURL.hash='ask-question';ask.href=askURL.href;
            if(!terms(query).length){status.textContent='Enter a topic or question to find a place to begin.';host.removeAttribute('aria-busy');return;}
            status.textContent='Searching published studies…';host.setAttribute('aria-busy','true');
            try{
                const data=await getIndex(); if(current!==sequence)return;
                const groups=groupMatches(data,query);matching=groups.best;supporting=groups.supporting;
                if(!matching.length&&!supporting.length)status.textContent='No matching studies for “'+query+'”. Try a shorter phrase, browse the topics, or ask a question below.';
                else {
                    bestHeading.hidden=!matching.length;appendResults(query);
                    if(supporting.length){related.hidden=false;summary.textContent='Supporting references ('+supporting.length+')';related.open=!matching.length;appendResults(query,true);}
                }
            }catch(_){if(current!==sequence)return;status.textContent='Search could not load. Please try again, or browse the topics below.';retry.hidden=false;}
            if(current===sequence)host.removeAttribute('aria-busy');
        }
        f.addEventListener('submit',e=>{e.preventDefault();const url=new URL(root.location.href);url.searchParams.set('q',input.value.trim().slice(0,200));root.history.pushState(null,'',url);run();});
        more.addEventListener('click',()=>{const first=host.children.length;appendResults(activeQuery);const link=host.children[first]?.querySelector('h2 a');if(link)link.focus();});
        relatedMore.addEventListener('click',()=>{const first=relatedHost.children.length;appendResults(activeQuery,true);relatedHost.children[first]?.querySelector('h2 a')?.focus();});
        retry.addEventListener('click',run);root.addEventListener('popstate',run);run();
    }
    function init(){
        initHeader();initResults();
        if(root.location.pathname.endsWith('/ask.html')){
            const query=new URL(root.location.href).searchParams.get('search-question'); const input=doc.getElementById('userInput');
            if(query && input && !input.value){input.value=query.trim().slice(0,200);input.dispatchEvent(new Event('input',{bubbles:true}));}
        }
    }
    if(doc.readyState==='loading')doc.addEventListener('DOMContentLoaded',init,{once:true});else init();
})(typeof window!=='undefined'?window:null);
