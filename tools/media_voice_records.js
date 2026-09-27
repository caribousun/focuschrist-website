// Extract only the actual data initializer, never execute visitor interaction code.
'use strict';
const fs=require('node:fs'), path=require('node:path'), vm=require('node:vm');
function extractRecords(source) {
    const start=source.indexOf('    const records = {');
    const end=source.indexOf('    const script = document.currentScript;', start);
    if(start<0 || end<0) throw new Error('Hero record boundaries changed; audit extractor must be reviewed');
    const context=Object.create(null);
    vm.runInNewContext(source.slice(start,end)+';globalThis.result=records;',context,{timeout:1000,contextCodeGeneration:{strings:false,wasm:false}});
    for(const [key,record] of Object.entries(context.result)) {
        if(typeof record.title!=='string' || !Array.isArray(record.paragraphs) || !record.paragraphs.length || record.paragraphs.some(p=>typeof p!=='string')) throw new Error('Incomplete public hero record: '+key);
    }
    return context.result;
}
if(require.main===module) process.stdout.write(JSON.stringify(extractRecords(fs.readFileSync(path.join(__dirname,'..','hero-details.js'),'utf8'))));
module.exports={extractRecords};
