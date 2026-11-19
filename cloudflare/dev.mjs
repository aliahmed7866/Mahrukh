import {createServer} from 'node:http';
import {readFileSync,mkdirSync} from 'node:fs';
import {localDB} from './local-db.mjs';
import {defaults} from './content.mjs';
import worker,{hash} from './worker.mjs';
const folder=new URL('./.local/',import.meta.url);mkdirSync(folder,{recursive:true});const DB=localDB(new URL('site.sqlite',folder).pathname);DB.raw.exec(readFileSync(new URL('./schema.sql',import.meta.url),'utf8'));
DB.raw.prepare('INSERT OR IGNORE INTO site(id,draft,published) VALUES(1,?,?)').run(JSON.stringify(defaults),JSON.stringify(defaults));
// This token is for the local development database only. Production setup uses a fresh random token.
DB.raw.prepare('INSERT OR IGNORE INTO setup(id,token_hash,expires) VALUES(1,?,?)').run(await hash('a'.repeat(64)),Date.now()+86400000);
const port=Number(process.env.PORT||3000),host=process.env.HOST||'0.0.0.0';
createServer(async(req,res)=>{try{const bytes=[];for await(const chunk of req)bytes.push(chunk);const url='http://'+req.headers.host+req.url;const response=await worker.fetch(new Request(url,{method:req.method,headers:req.headers,...(!['GET','HEAD'].includes(req.method)?{body:Buffer.concat(bytes)}:{})}),{DB,AUTH_PEPPER:'local'});res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));}catch(error){res.writeHead(500);res.end('Development server error');}}).listen(port,host,()=>console.log(`Mahrukh preview: http://${host}:${port}`));
