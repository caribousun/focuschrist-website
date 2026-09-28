function inspectCfmPalette(){
 if(!document.body.classList.contains('cfm-page'))return {checked:0,failures:[]};
 const probe=document.createElement('span');probe.style.cssText='position:fixed;visibility:hidden;color:var(--fc-text);background:var(--fc-bg-deep)';document.body.append(probe);const ps=getComputedStyle(probe),expected={color:ps.color,backgroundColor:ps.backgroundColor};probe.remove();
 const nodes=[...document.querySelectorAll('main .cfm-btn:not(.cfm-btn--gold),main .fc-button:not(.fc-button--primary),main .cfm-reading-range>summary,main .cfm-reading-chapters>a,main [data-cfm-current-reading]>a,main .cfm-schedule-reading>a,main .cfm-jump>a,main .cfm-week-nav>button,main .cfm-path__body>a,main .cfm-text-link,main .cfm-source-link,main .fc-study-visual-sources>a')],failures=[];
 for(const n of nodes){const s=getComputedStyle(n),solid=n.matches('.cfm-jump>a,.cfm-week-nav>button');if(s.color!==expected.color||s.backgroundImage!=='none'||(solid?s.backgroundColor!==expected.backgroundColor:!['rgba(0, 0, 0, 0)','transparent'].includes(s.backgroundColor)))failures.push({text:n.textContent.trim().slice(0,90),color:s.color,backgroundImage:s.backgroundImage,backgroundColor:s.backgroundColor});}
 for(const reading of document.querySelectorAll('[data-cfm-current-reading],.cfm-schedule-reading'))if(getComputedStyle(reading).backgroundColor!==expected.backgroundColor)failures.push({text:'Reading group lacks navy contrast'});
 return {checked:nodes.length,expected,failures};
}
module.exports={inspectCfmPalette};
