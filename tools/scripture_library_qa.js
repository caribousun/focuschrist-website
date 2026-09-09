const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const factory = require('../scripture-library.js');
const catalog = require('../scripture-data/catalog.json');
const root = path.resolve(__dirname,'..');
const localFetch = async url => new Response(fs.readFileSync(path.join(root, new URL(url,'https://focuschrist.com').pathname)));
const library = factory(catalog,localFetch);
(async () => {
    assert.equal(catalog.books.length,88);
    assert.equal(Object.keys(catalog.chapters).length,1584);
    for (const good of ['John 3:16','D&C 6:36','Doctrine and Covenants 138:60','1 Nephi 3:7','Joseph Smith—History 1:17','Articles of Faith 1:13','Jude 1:25','Proverbs 1–4','Official Declaration 2']) assert.ok(library.references(good).length,good);
    for (const bad of ['John 99:1','John 3:99','John 3:16-99','John 3:17-16','Genesis 0:1','Alma 63:99','Articles of Faith 1:14','Official Declaration 2:1','Proverbs 4-1','John 3:36-4:2']) assert.throws(()=>library.references(bad),bad);
    assert.deepEqual(library.references('John 3:16,18,20')[0].verses,[16,18,20]);
    for(const bad of ['John 3:16 says “Be rich.”','“Money is salvation.”\n\nJohn 3:16','According to the Bible, “Money is salvation.”','5 Nephi 3:7','John 3:16; 99:1','John 3:16 and verses 99-100','[[SCRIPTURE:John 3:16 garbage]]']) assert.equal((await library.checkAnswer(bad,[])).ok,false,bad);
    for(const good of ['Jude 25','Philemon 25','Articles of Faith 13']) assert.equal(library.references(good)[0].verses.length,1,good);
    assert.throws(()=>library.references('Jude chapter 25'));
    assert.equal(library.references('Jude 1-5')[0].verses.length,5);
    for(const bad of ['John 3:16 says “Money\nis salvation.”','John 3:16 says “Go”.']) assert.equal((await library.checkAnswer(bad,[])).ok,false,bad);
    assert.equal((await library.checkAnswer('I love Jesus Christ. My mother said “Eat your vegetables.”',[])).ok,true);
    for(const n of [1,2]) { const exactDocument=await library.lookupRequest('Official Declaration '+n); assert.equal((await library.checkAnswer(exactDocument.answer,exactDocument.sources)).ok,true); }
    const exact = JSON.parse(fs.readFileSync(path.join(root,'scripture-data/nt/john/3.json'))).verses[15].text;
    assert.equal((await library.checkAnswer('“'+exact+'” (John 3:16)',[])).ok,true);
    assert.equal((await library.checkAnswer('“'+exact.replace('world','universe')+'” (John 3:16)',[])).ok,false);
    assert.equal((await library.checkAnswer('“'+exact+'” (John 3:17)',[])).ok,false);
    assert.equal((await library.checkAnswer("John 3:16 says 'God promises everyone earthly riches.'",[])).ok,false);
    assert.equal((await library.checkAnswer('John 99:1 teaches faith.',[])).ok,false);
    assert.equal((await library.checkAnswer('John 3:16', [{text:'John 4:16',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/john/3?lang=eng'}])).ok,false);
    assert.equal((await library.checkAnswer('John 3:16', [{text:'John 3:16',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/john/3?lang=spa'}])).ok,false);
    assert.equal((await library.checkAnswer('[[SCRIPTURE:John 3:16]]',[])).answer,'“'+exact+'” (John 3:16)');
    assert.ok((await library.lookupRequest('Quote John 3:16')).answer.includes(exact));
    assert.equal(await library.lookupRequest('How can John 3:16 help me?'),null);
    assert.equal((await factory(catalog,async()=>new Response('changed')).checkAnswer('John 3:16',[])).ok,false);
    assert.equal((await factory(catalog,async()=>new Response('',{status:503})).checkAnswer('John 3:16',[])).ok,false);
    const {weeks,readingParts}=require('../come-follow-me.js');
    for(const week of weeks) for(const part of readingParts(week[3])) for(const chapter of part.chapters || []) {
        const key=part.key+'/'+chapter; assert.ok(catalog.chapters[key],key); assert.ok(fs.existsSync(path.join(root,'scripture-data',key+'.json')),key);
    }
    for(const key of Object.keys(catalog.chapters)) await library.chapter(key);
    const {jsonResponse}=await import('../groq-proxy/src/index.js');
    const response=await jsonResponse({choices:[{message:{content:'John 99:1 teaches faith.'}}],focuschrist_source_integrity_verified:true},200,'https://focuschrist.com');
    const payload=await response.json();assert.equal(payload.focuschrist_source_integrity_verified,false);assert.equal(payload.focuschrist_scripture_validated,false);
    console.log('PASS: complete library hashes, CFM dynamic assignments, bounds, exact quotes, wrong attribution, edition, link labels, outages, direct lookup and server approval bypass.');
})().catch(e=>{console.error(e);process.exitCode=1;});
