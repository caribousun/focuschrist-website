const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..');
function setup(){
 const dom=new JSDOM(fs.readFileSync(path.join(root,'answers/holy-ghost.html'),'utf8'),{url:'https://focuschrist.com/answers/holy-ghost.html',runScripts:'outside-only'});
 const timers=[];dom.window.setTimeout=f=>{timers.push(f);return timers.length;};dom.window.clearTimeout=id=>{timers[id-1]=null;};
 dom.window.eval(fs.readFileSync(path.join(root,'holy-ghost-video.js'),'utf8'));
 return {dom,d:dom.window.document,timers};
}
test('player is opt-in, exact owner video loads, and close destroys it',async()=>{
 const {dom,d}=setup();let options,destroyed=0;
 assert.equal(d.querySelectorAll('#holy-ghost-video iframe').length,0);
 assert.equal(d.querySelectorAll('script[src="https://www.youtube.com/iframe_api"]').length,0);
 dom.window.YT={Player:function(mount,o){options=o;const frame=d.createElement('iframe');mount.replaceWith(frame);this.destroy=()=>{destroyed++;frame.remove();};}};
 d.querySelector('[data-video-preview]').click();await Promise.resolve();
 assert.equal(options.videoId,'AGS45Fd9nmE');assert.equal(options.playerVars.autoplay,0);
 const frame=d.querySelector('#holy-ghost-video iframe');options.events.onReady({target:{getIframe:()=>frame}});
 assert.match(frame.title,/David A. Bednar/);assert.match(d.querySelector('[data-video-status]').textContent,/player is ready/);
 d.querySelector('[data-video-close]').click();assert.equal(destroyed,1);assert.equal(d.querySelector('[data-video-preview]').hidden,false);assert.equal(d.querySelector('#holy-ghost-video iframe'),null);
 dom.window.close();
});
test('timeout restores preview with real YouTube fallback and stale readiness cannot reopen it',async()=>{
 const {dom,d,timers}=setup();let options;
 dom.window.YT={Player:function(mount,o){options=o;this.destroy=()=>{};}};
 d.querySelector('[data-video-preview]').click();await Promise.resolve();timers[0]();
 assert.match(d.querySelector('[data-video-status]').textContent,/did not become ready/);
 assert.equal(d.querySelector('[data-video-preview]').hidden,false);
 options.events.onReady({target:{getIframe:()=>null}});
 assert.match(d.querySelector('[data-video-status]').textContent,/did not become ready/);
 assert.equal(d.querySelector('.hg-video__controls a').href,'https://www.youtube.com/watch?v=AGS45Fd9nmE');dom.window.close();
});
test('API load error and provider playback error both preserve usable fallback',async()=>{
 const first=setup();first.d.querySelector('[data-video-preview]').click();first.d.querySelector('script[src="https://www.youtube.com/iframe_api"]').dispatchEvent(new first.dom.window.Event('error'));
 await Promise.resolve();await Promise.resolve();assert.match(first.d.querySelector('[data-video-status]').textContent,/could not load/);first.dom.window.close();
 const {dom,d}=setup();let options;dom.window.YT={Player:function(m,o){options=o;this.destroy=()=>{};}};
 d.querySelector('[data-video-preview]').click();await Promise.resolve();options.events.onError({data:101});
 assert.match(d.querySelector('[data-video-status]').textContent,/could not play here/);assert.equal(d.querySelector('[data-video-stage]').hidden,true);dom.window.close();
});
