import {defaults,validateDocument,publicDocument,InputError,COPY_FIELDS,ARTS,ARTWORK,SECTIONS} from './content.mjs';
import {renderPage,renderStudio} from './render.mjs';
import {assets} from './assets.mjs';
const enc=new TextEncoder();
export async function hash(text){return hex(await crypto.subtle.digest('SHA-256',enc.encode(text)));}
const hex=b=>[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('');
const token=()=>hex(crypto.getRandomValues(new Uint8Array(32)));
export async function passwordHash(password,salt){const key=await crypto.subtle.importKey('raw',enc.encode(password),'PBKDF2',false,['deriveBits']);return hex(await crypto.subtle.deriveBits({name:'PBKDF2',salt:enc.encode(salt),iterations:100000,hash:'SHA-256'},key,256));}
function constantEqual(a,b){if(a.length!==b.length)return false;let out=0;for(let i=0;i<a.length;i++)out|=a.charCodeAt(i)^b.charCodeAt(i);return out===0;}
const json=(data,status=200,headers={})=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json;charset=utf-8','Cache-Control':'no-store',...headers}});
const html=(value,status=200)=>new Response(value,{status,headers:{'Content-Type':'text/html;charset=utf-8','Cache-Control':'no-store'}});
const cookie=(value,age=43200)=>`__Host-mahrukh=${value}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${age}`;
async function boundedBody(request,max){const reader=request.body?.getReader();if(!reader)return new Uint8Array();let size=0,chunks=[];for(;;){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>max){await reader.cancel();throw new InputError('This upload is too large.',413);}chunks.push(value);}const bytes=new Uint8Array(size);let offset=0;for(const x of chunks){bytes.set(x,offset);offset+=x.length;}return bytes;}
async function bodyJSON(request){if(!request.headers.get('Content-Type')?.startsWith('application/json'))throw new InputError('Send JSON content.',415);try{return JSON.parse(new TextDecoder().decode(await boundedBody(request,450000)));}catch(error){if(error instanceof InputError)throw error;throw new InputError('The submitted content could not be read.');}}
async function state(env){const row=await env.DB.prepare('SELECT * FROM site WHERE id=1').first();if(!row)throw new Error('Site is not initialized');return {...row,draft:JSON.parse(row.draft),published:JSON.parse(row.published)};}
async function session(request,env){const raw=request.headers.get('Cookie')?.match(/(?:^|;\s*)__Host-mahrukh=([a-f0-9]{64})(?:;|$)/)?.[1];if(!raw)return null;const key=await hash(raw);const row=await env.DB.prepare('SELECT * FROM sessions WHERE token_hash=? AND expires>?').bind(key,Date.now()).first();return row;}
async function requireOwner(request,env){const s=await session(request,env);if(!s)throw new InputError('Please sign in again. Your unsaved changes are still on this page.',401);if(request.method!=='GET'&&request.headers.get('X-CSRF-Token')!==s.csrf)throw new InputError('Reload the studio before saving.',403);return s;}
async function rateLimit(request,env){const key=await hash((request.headers.get('CF-Connecting-IP')||'local')+'|'+(env.AUTH_PEPPER||'local-test'));const now=Date.now();await env.DB.prepare('DELETE FROM attempts WHERE expires<?').bind(now).run();const row=await env.DB.prepare('INSERT INTO attempts(key,count,expires) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1 RETURNING count').bind(key,now+15*60*1000).first();if(row.count>12)throw new InputError('Too many attempts. Try again in 15 minutes.',429);}
async function createSession(env){const raw=token(),csrf=token();await env.DB.prepare('DELETE FROM sessions WHERE expires<?').bind(Date.now()).run();await env.DB.prepare('INSERT INTO sessions(token_hash,csrf,expires) VALUES(?,?,?)').bind(await hash(raw),csrf,Date.now()+43200000).run();return {raw,csrf};}
export function cleanJpeg(bytes){
 if(bytes.length>300000)throw new InputError('Choose a photo smaller than 300 KB after resizing.',413);
 const fail=()=>{throw new InputError('Choose a valid JPEG photo.');};if(bytes.length<30||bytes[0]!==255||bytes[1]!==216)fail();let pos=2,width=0,height=0,scans=0,quant=false,huffman=false,ended=false;const parts=[bytes.slice(0,2)];
 while(pos<bytes.length){const start=pos;if(bytes[pos++]!==255)fail();while(bytes[pos]===255)pos++;const marker=bytes[pos++];if(marker===undefined||marker===0||marker===216||(marker>=208&&marker<=215))fail();if(marker===217){if(!scans||!width||!quant||!huffman)fail();parts.push(new Uint8Array([255,217]));ended=true;break;}if(pos+2>bytes.length)fail();const len=bytes[pos]*256+bytes[pos+1],end=pos+len;if(len<2||end>bytes.length)fail();if([192,194].includes(marker)){if(width||len<11||bytes[pos+2]!==8)fail();height=bytes[pos+3]*256+bytes[pos+4];width=bytes[pos+5]*256+bytes[pos+6];const c=bytes[pos+7];if(![1,3].includes(c)||len!==8+3*c||!width||!height||width>2400||height>2400)fail();}else if(marker>=192&&marker<=207&&marker!==196)fail();if(marker===219)quant=true;if(marker===196)huffman=true;if(!(marker>=224&&marker<=239)&&marker!==254)parts.push(bytes.slice(start,end));pos=end;
 if(marker===218){if(!width||!quant||!huffman)fail();scans++;const begin=pos;while(pos<bytes.length){if(bytes[pos]!==255){pos++;continue;}let next=pos+1;while(bytes[next]===255)next++;if(bytes[next]===0||(bytes[next]>=208&&bytes[next]<=215)){pos=next+1;continue;}break;}if(pos===begin)fail();parts.push(bytes.slice(begin,pos));}}
 if(!ended)fail();const output=new Uint8Array(parts.reduce((n,x)=>n+x.length,0));let at=0;parts.forEach(x=>{output.set(x,at);at+=x.length;});return output;
}
async function route(request,env){
 const url=new URL(request.url),path=url.pathname.replace(/\/$/,'')||'/';
 if(!['GET','HEAD','POST'].includes(request.method))return json({error:'Method not allowed'},405,{'Allow':'GET, HEAD, POST'});
 // Keep one public origin without forwarding credentials or POST bodies between hosts.
 if(env.APP_ORIGIN&&url.origin!==env.APP_ORIGIN){
  const primary=new URL(env.APP_ORIGIN),aliases=(env.REDIRECT_HOSTS||'').split(',').map(x=>x.trim());
  if(url.hostname!==primary.hostname&&!aliases.includes(url.hostname))return json({error:'Unknown website address.'},421);
  if(request.method==='POST')return json({error:'Open the studio at '+primary.origin+'/studio and sign in again before saving.'},409);
  primary.pathname=url.pathname;primary.search=url.search;
  return new Response(null,{status:308,headers:{Location:primary.href,'Cache-Control':'no-store'}});
 }
 if(request.method==='POST'&&(request.headers.get('Origin')!==url.origin||request.headers.get('Sec-Fetch-Site')==='cross-site'))throw new InputError('Use the studio on this website to make changes.',403);
 if(path==='/health')return json({ok:!!(await env.DB.prepare('SELECT id FROM site WHERE id=1').first()),version:'1.0.0'});
 if(request.method==='POST'&&['/api/login','/api/setup'].includes(path)){
  await rateLimit(request,env);const b=await bodyJSON(request);if(typeof b.password!=='string'||b.password.length<12||b.password.length>128)throw new InputError('Use a password of 12–128 characters.');
  if(path==='/api/setup'){if(typeof b.token!=='string'||!/^[a-f0-9]{64}$/.test(b.token))throw new InputError('Use your private setup link.',403);const salt=token(),pw=await passwordHash(b.password,salt);const row=await env.DB.prepare('INSERT INTO owner(id,password,salt) SELECT 1,?,? FROM setup WHERE id=1 AND token_hash=? AND expires>? AND NOT EXISTS(SELECT 1 FROM owner) ON CONFLICT(id) DO NOTHING').bind(pw,salt,await hash(b.token),Date.now()).run();if(!row.meta.changes)throw new InputError('This setup link has expired or has already been used.',403);await env.DB.prepare('DELETE FROM setup WHERE id=1').run();}
  else{const owner=await env.DB.prepare('SELECT * FROM owner WHERE id=1').first();const candidate=await passwordHash(b.password,owner?.salt||'dummy-salt');if(!owner||!constantEqual(candidate,owner.password))throw new InputError('Password not recognised.',401);}
  const s=await createSession(env);return json({ok:true,csrf:s.csrf},200,{'Set-Cookie':cookie(s.raw)});
 }
 if(path==='/api/session'){const s=await session(request,env);return json({signedIn:!!s,csrf:s?.csrf||''});}
 if(path.startsWith('/api/')){
  const s=await requireOwner(request,env);
  if(path==='/api/validate'&&request.method==='POST')return json({document:validateDocument((await bodyJSON(request)).document)});
  if(path==='/api/site'&&request.method==='GET'){const row=await state(env);return json({...row,fields:COPY_FIELDS,arts:ARTS,artwork:ARTWORK,sections:SECTIONS});}
  if(path==='/api/history'&&request.method==='GET'){const r=await env.DB.prepare('SELECT version,document,created_at FROM history ORDER BY version DESC').all();return json(r.results.map(x=>({...x,document:JSON.parse(x.document)})));}
  if(path==='/api/media'&&request.method==='GET'){const r=await env.DB.prepare('SELECT id,size FROM media ORDER BY created_at DESC').all();return json(r.results);}
  if(path==='/api/site'&&request.method==='POST'){
   const b=await bodyJSON(request);if(!Number.isSafeInteger(b.version)||!['save','publish'].includes(b.action))throw new InputError('Reload before saving.');const doc=validateDocument(b.document);
   for(const img of new Set(doc.items.map(x=>x.image).filter(Boolean))){if(!await env.DB.prepare('SELECT id FROM media WHERE id=?').bind(img.slice(7)).first())throw new InputError('One of these photos is unavailable. Upload it again.');}
   const serialized=JSON.stringify(doc);const result=await env.DB.prepare('UPDATE site SET draft=?,published=CASE WHEN ?=1 THEN ? ELSE published END,version=version+1,updated_at=CURRENT_TIMESTAMP WHERE id=1 AND version=?').bind(serialized,b.action==='publish'?1:0,serialized,b.version).run();if(!result.meta.changes)throw new InputError('The website changed in another tab. Export your edits before reloading; your changes are still here.',409);return json(await state(env));
  }
  if(path==='/api/media'&&request.method==='POST'){
   if(!request.headers.get('Content-Type')?.startsWith('image/jpeg'))throw new InputError('Upload a JPEG photo.',415);const bytes=cleanJpeg(await boundedBody(request,300000));const id=crypto.randomUUID();
   const result=await env.DB.prepare('INSERT INTO media(id,bytes,size) SELECT ?,?,? WHERE (SELECT COUNT(*) FROM media)<100 AND (SELECT COALESCE(SUM(size),0) FROM media)+?<=15000000').bind(id,bytes.buffer,bytes.length,bytes.length).run();if(!result.meta.changes)throw new InputError('Your photo space is full (15 MB / 100 photos). Remove unused photos first.',409);return json({id,url:'/media/'+id},201);
  }
  if(path==='/api/media/delete'&&request.method==='POST'){const b=await bodyJSON(request);if(!/^[a-f0-9-]{36}$/.test(b.id))throw new InputError('Choose a photo.');const pattern='%/media/'+b.id+'%';const result=await env.DB.prepare('DELETE FROM media WHERE id=? AND NOT EXISTS(SELECT 1 FROM site WHERE draft LIKE ? OR published LIKE ?) AND NOT EXISTS(SELECT 1 FROM history WHERE document LIKE ? OR published LIKE ?)').bind(b.id,pattern,pattern,pattern,pattern).run();if(!result.meta.changes)throw new InputError('This photo is used by the website or a saved version.',409);return json({ok:true});}
  if(path==='/api/logout'&&request.method==='POST'){await env.DB.prepare('DELETE FROM sessions WHERE token_hash=?').bind(s.token_hash).run();return json({ok:true},200,{'Set-Cookie':cookie('',0)});}
  if(path==='/api/password'&&request.method==='POST'){const b=await bodyJSON(request);if(typeof b.current!=='string'||b.current.length>128||typeof b.password!=='string'||b.password.length<12||b.password.length>128)throw new InputError('Use a new password of 12–128 characters.');await rateLimit(request,env);const owner=await env.DB.prepare('SELECT * FROM owner WHERE id=1').first();if(!constantEqual(await passwordHash(b.current,owner.salt),owner.password))throw new InputError('Current password not recognised.',401);const salt=token();await env.DB.batch([env.DB.prepare('UPDATE owner SET password=?,salt=? WHERE id=1').bind(await passwordHash(b.password,salt),salt),env.DB.prepare('DELETE FROM sessions')]);return json({ok:true},200,{'Set-Cookie':cookie('',0)});}
  return json({error:'Not found'},404);
 }
 if(request.method==='POST')return json({error:'Not found'},404);
 if(path.startsWith('/media/')){const row=await state(env);const visible=row.published.items.some(x=>x.visible&&x.image===path);if(!visible&&!await session(request,env))return new Response('Not found',{status:404});const media=await env.DB.prepare('SELECT bytes FROM media WHERE id=?').bind(path.slice(7)).first();if(!media)return new Response('Not found',{status:404});// D1 reads BLOBs as number arrays; Response needs binary bytes.
 const bytes=Array.isArray(media.bytes)?Uint8Array.from(media.bytes):media.bytes;return new Response(bytes,{headers:{'Content-Type':'image/jpeg','Cache-Control':'no-store'}});}
 if(assets[path]){const a=assets[path],bytes=Uint8Array.from(atob(a.body),x=>x.charCodeAt(0));return new Response(bytes,{headers:{'Content-Type':a.type,'Cache-Control':'public,max-age=0,must-revalidate','ETag':a.etag}});}
 if(['/studio','/admin'].includes(path))return html(renderStudio());
 if(path==='/robots.txt')return new Response(`User-agent: *\nDisallow: /studio\nDisallow: /admin\nDisallow: /api/\nDisallow: /preview\nSitemap: ${url.origin}/sitemap.xml`,{headers:{'Content-Type':'text/plain'}});
 const row=await state(env);
 if(path==='/sitemap.xml'){const paths=['/','/collection','/our-roots','/contact','/fabric-and-fit',...row.published.items.filter(x=>x.visible).map(x=>'/piece/'+x.id)];return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${paths.map(p=>`<url><loc>${url.origin}${p}</loc></url>`).join('')}</urlset>`,{headers:{'Content-Type':'application/xml'}});}
 const preview=path==='/preview';if(preview)await requireOwner(request,env);
 const page=renderPage(preview?row.draft:row.published,{path:preview?'/':path,lang:url.searchParams.get('lang')==='ur'?'ur':'en',preview,origin:url.origin});return html(page.html,page.status);
}
export default {async fetch(request,env){let response;try{response=await route(request,env);}catch(error){response=json({error:error instanceof InputError?error.message:'Something went wrong. Please try again.'},error instanceof InputError?error.status:500);}const headers=new Headers(response.headers);headers.set('X-Content-Type-Options','nosniff');headers.set('Referrer-Policy','no-referrer');headers.set('Permissions-Policy','camera=(), microphone=(), geolocation=()');headers.set('X-Frame-Options','DENY');headers.set('Strict-Transport-Security','max-age=31536000');headers.set('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob: data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'");return new Response(request.method==='HEAD'?null:response.body,{status:response.status,headers});}};
