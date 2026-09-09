// Local browser review only. Public application files are never rewritten.
import http from 'node:http';
import path from 'node:path';
import {readFile, stat} from 'node:fs/promises';
const root=process.cwd(), endpoint=process.env.FOCUSCHRIST_QUESTION_PREVIEW;
if(!/^https:\/\/[a-z0-9-]+-focuschrist-groq-proxy\.caribousun\.workers\.dev\/?$/.test(endpoint||''))throw new Error('Set the isolated question-preview endpoint. Production endpoints are refused.');
const types={'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.webp':'image/webp','.jpg':'image/jpeg','.svg':'image/svg+xml','.woff2':'font/woff2','.txt':'text/plain'};
http.createServer(async(req,res)=>{
  try {
    const url=new URL(req.url,'http://127.0.0.1:4188');
    if(url.pathname==='/__question_review_ai') {
      if(req.method!=='POST'){res.writeHead(405);res.end();return;}
      let bytes=0, chunks=[];for await(const chunk of req){bytes+=chunk.length;if(bytes>120000)throw new Error('Request too large');chunks.push(chunk);}
      const upstream=await fetch(endpoint,{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:Buffer.concat(chunks),signal:AbortSignal.timeout(70000)});
      res.writeHead(upstream.status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(await upstream.text());return;
    }
    if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return;}
    const pathname=decodeURIComponent(url.pathname);
    if(pathname.split('/').some(part=>part.startsWith('.'))||/^\/(?:groq-proxy|tools|docs)\//.test(pathname))throw new Error('Private path');
    let file=path.resolve(root,'.'+pathname);
    if(!file.startsWith(root+path.sep)&&file!==root)throw new Error('Invalid path');
    if((await stat(file)).isDirectory())file=path.join(file,'index.html');
    const extension=path.extname(file);let data=await readFile(file);
    if(extension==='.js'||extension==='.html')data=Buffer.from(data.toString('utf8').replaceAll('https://focuschrist-groq-proxy.caribousun.workers.dev','/__question_review_ai'));
    res.writeHead(200,{'Content-Type':types[extension]||'application/octet-stream','Cache-Control':'no-store'});res.end(req.method==='HEAD'?undefined:data);
  }catch(error){res.writeHead(503,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify({error:'Local review request unavailable'}));}
}).listen(4188,'127.0.0.1',()=>console.log('Local candidate review: http://127.0.0.1:4188/ask.html and /pioneers.html; isolated backend '+endpoint));
