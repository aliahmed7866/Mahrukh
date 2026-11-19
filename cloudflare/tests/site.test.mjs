import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {localDB} from '../local-db.mjs';
import worker,{hash,cleanJpeg} from '../worker.mjs';
import {defaults,validateDocument,publicDocument} from '../content.mjs';
import {renderPage} from '../render.mjs';
const origin='https://mahrukh.test',setupToken='b'.repeat(64),password='a long unique test password';
function fixture(){const DB=localDB();DB.raw.exec(readFileSync(new URL('../schema.sql',import.meta.url),'utf8'));DB.raw.prepare('INSERT INTO site(id,draft,published) VALUES(1,?,?)').run(JSON.stringify(defaults),JSON.stringify(defaults));return {DB,AUTH_PEPPER:'test-only'};}
function call(env,path,{method='GET',body,cookie,csrf,originHeader=origin,type='application/json'}={}){return worker.fetch(new Request(origin+path,{method,headers:{Origin:originHeader,...(cookie?{Cookie:cookie}:{}),...(csrf?{'X-CSRF-Token':csrf}:{}),...(body!==undefined?{'Content-Type':type}:{})},body:body===undefined?undefined:typeof body==='string'||body instanceof Uint8Array?body:JSON.stringify(body)}),env);}
async function signIn(env){env.DB.raw.prepare('INSERT INTO setup VALUES(1,?,?)').run(await hash(setupToken),Date.now()+60000);const r=await call(env,'/api/setup',{method:'POST',body:{token:setupToken,password}});assert.equal(r.status,200);const data=await r.json();return {cookie:r.headers.get('Set-Cookie').split(';')[0],csrf:data.csrf};}
const newDoc=()=>structuredClone(defaults);
test('studio loads its shared product builder as a JavaScript module',async()=>{
 const env=fixture(),response=await call(env,'/product-builder.mjs');
 assert.equal(response.status,200);
 assert.match(response.headers.get('Content-Type'),/^text\/javascript/);
 assert.equal(await response.text(),readFileSync(new URL('../public/product-builder.mjs',import.meta.url),'utf8'));
 const script=await(await call(env,'/studio.js')).text();
 assert.match(script,/from '\.\/product-builder\.mjs'/);
});
test('uploaded photographs return exact JPEG bytes from D1 for owner previews and published products',async()=>{
 const env=fixture(),auth=await signIn(env);
 const original=new Uint8Array(readFileSync(new URL('./fixtures/photo.jpg',import.meta.url)));
 const uploaded=await call(env,'/api/media',{...auth,method:'POST',body:original,type:'image/jpeg'});
 assert.equal(uploaded.status,201);
 const {id,url}=await uploaded.json(),expected=cleanJpeg(original);
 const stored=await env.DB.prepare('SELECT bytes FROM media WHERE id=?').bind(id).first();
 assert.ok(Array.isArray(stored.bytes),'Exercise the production D1 BLOB representation');
 const checkImage=async options=>{
  const response=await call(env,url,options);
  assert.equal(response.status,200);
  assert.equal(response.headers.get('Content-Type'),'image/jpeg');
  assert.equal(response.headers.get('Cache-Control'),'no-store');
  const actual=new Uint8Array(await response.arrayBuffer());
  assert.deepEqual(actual,expected,'Return JPEG bytes, not an empty body or comma-separated numbers');
 };
 assert.equal((await call(env,url)).status,404);
 await checkImage(auth);
 const doc=newDoc();doc.items[0].kind='piece';doc.items[0].image=url;
 assert.equal((await call(env,'/api/site',{...auth,method:'POST',body:{document:doc,version:1,action:'publish'}})).status,200);
 await checkImage();
 for(const path of ['/collection','/piece/'+doc.items[0].id])assert.ok((await(await call(env,path)).text()).includes(`src="${url}"`));
 const head=await call(env,url,{method:'HEAD'});
 assert.equal(head.status,200);assert.equal((await head.arrayBuffer()).byteLength,0);
 doc.items[0].visible=false;
 assert.equal((await call(env,'/api/site',{...auth,method:'POST',body:{document:doc,version:2,action:'publish'}})).status,200);
 assert.equal((await call(env,url)).status,404);
 await checkImage(auth);
});
test('empty catalogue is visible in English and Urdu without turning artwork or hidden pieces into products',()=>{
 const doc=newDoc();doc.mode='catalogue';doc.whatsapp='923001234567';
 doc.items.push({...doc.items[0],id:'private-piece',title:'Private unfinished piece',kind:'piece',visible:false});
 for(const path of ['/','/collection']){
  const html=renderPage(doc,{path}).html;
  assert.match(html,/The Mahrukh collection/);assert.match(html,/Clothing pieces are coming soon/);
  assert.match(html,/Chat on WhatsApp/);assert.match(html,/From our notebook/);
  assert.doesNotMatch(html,/class="piece-card"|Private unfinished piece|role="search"/);
  assert.match(renderPage(doc,{path,lang:'ur'}).html,/ملبوسات جلد شامل کیے جائیں گے/);
 }
 doc.copy.en.collectionTitle='My own collection';
 assert.match(renderPage(doc).html,/My own collection/);
 doc.mode='portfolio';assert.doesNotMatch(renderPage(doc).html,/Clothing pieces are coming soon/);
});
test('unfinished clothing pieces can be saved privately but need a photograph before appearing',()=>{
 const doc=newDoc();doc.items[0].kind='piece';doc.items[0].visible=false;
 assert.equal(validateDocument(doc).items[0].kind,'piece');
 assert.equal(renderPage(doc,{path:'/piece/indigo-stories'}).status,404);
 doc.items[0].visible=true;assert.throws(()=>validateDocument(doc),/real photograph/);
});
test('decorative notes have no shopping controls; real pieces retain their gallery and enquiry flow',()=>{
 const doc=newDoc();
 let html=renderPage(doc,{path:'/piece/a-courtyard-in-bloom'}).html;
 assert.match(html,/journal-article/);assert.doesNotMatch(html,/data-save=|data-zoom|data-share|class="price"|Ask about this piece/);
 const real={...doc.items[0],id:'real-piece',title:'A real piece',kind:'piece',image:'/media/'+crypto.randomUUID(),price:3000};
 doc.items.push(real);doc.mode='catalogue';doc.whatsapp='923001234567';
 doc.copy.en.delivery='Delivery agreed before ordering.';doc.copy.en.returns='Returns agreed before ordering.';
 html=renderPage(doc).html;
 assert.equal((html.match(/class="piece-card"/g)||[]).length,1);assert.match(html,/role="search"/);assert.match(html,/PKR 3,000/);
 assert.equal((html.match(/class="journal-note"/g)||[]).length,4);assert.doesNotMatch(html,/data-save="indigo-stories"/);
 html=renderPage(doc,{path:'/piece/real-piece'}).html;
 assert.match(html,/data-zoom/);assert.match(html,/data-save="real-piece"/);assert.match(html,/Ask about this piece/);
});
test('custom domain redirects keep paths, language and setup fragments without forwarding writes',async()=>{
 const env={...fixture(),APP_ORIGIN:'https://mahrukh.uk',REDIRECT_HOSTS:'www.mahrukh.uk,mahrukh.ammeemughal.workers.dev'};
 for(const alias of ['https://www.mahrukh.uk','https://mahrukh.ammeemughal.workers.dev','http://mahrukh.uk']){
  for(const path of ['/collection?lang=ur','/studio','//untrusted.example/path']){
   const r=await worker.fetch(new Request(alias+path),env);
   assert.equal(r.status,308);assert.equal(r.headers.get('Location'),'https://mahrukh.uk'+path);
   assert.equal(new URL(r.headers.get('Location')).hash,''); // A redirect with no fragment inherits the original browser fragment.
  }
  const write=await worker.fetch(new Request(alias+'/api/site',{method:'POST',headers:{Origin:alias}}),env);
  assert.equal(write.status,409);assert.equal(write.headers.get('Location'),null);
 }
 assert.equal((await worker.fetch(new Request('https://untrusted.example/'),env)).status,421);
 const home=await worker.fetch(new Request('https://mahrukh.uk/'),env);
 assert.equal(home.status,200);assert.match(await home.text(),/rel="canonical" href="https:\/\/mahrukh.uk\//);
 const sitemap=await (await worker.fetch(new Request('https://mahrukh.uk/sitemap.xml'),env)).text();
 assert.match(sitemap,/<loc>https:\/\/mahrukh.uk\/collection<\/loc>/);assert.doesNotMatch(sitemap,/workers.dev|www.mahrukh/);
 assert.equal((await worker.fetch(new Request('https://mahrukh.uk/api/login',{method:'POST',headers:{Origin:'https://www.mahrukh.uk'}}),env)).status,403);
 assert.equal(env.DB.raw.prepare('SELECT version FROM site').get().version,1);
});
test('public routes, accessibility structure, local assets and real 404',async()=>{const env=fixture();for(const path of ['/','/?lang=ur','/collection','/our-roots','/contact','/fabric-and-fit','/privacy','/piece/indigo-stories','/site.css','/site.js','/art/chai.svg','/art/courtyard-moment-640.webp','/art/courtyard-moment.webp','/art/threads.svg','/naskh.ttf','/robots.txt','/sitemap.xml']){const r=await call(env,path);assert.equal(r.status,200,path);assert.equal(r.headers.get('X-Content-Type-Options'),'nosniff');if(path.endsWith('.webp')){assert.equal(r.headers.get('Content-Type'),'image/webp');const bytes=new Uint8Array(await r.arrayBuffer());assert.equal(new TextDecoder().decode(bytes.slice(8,12)),'WEBP');}}const home=await (await call(env,'/')).text();assert.match(home,/<main id="main">/);assert.match(home,/srcset="[^"]+courtyard-moment.webp 1122w"/);assert.match(home,/threads.svg/);assert.match(home,/data-full-src="\/art\/courtyard-moment.webp"/);assert.match(home,/NOTES FROM OUR WORLD/);assert.doesNotMatch(home,/class="piece-card"|data-save=|role="search"/);assert.doesNotMatch(home,/PKR /);assert.match(await (await call(env,'/?lang=ur')).text(),/lang="ur" dir="rtl"/);assert.equal((await call(env,'/missing')).status,404);assert.equal((await call(env,'/piece/missing')).status,404);assert.equal((await call(env,'/preview')).status,401);assert.equal((await call(env,'/api/site')).status,401);assert.equal((await call(env,'/api/history')).status,401);});
test('first owner claims setup once; secure cookie, login and request boundaries',async()=>{const env=fixture();const auth=await signIn(env);assert.equal((await call(env,'/api/setup',{method:'POST',body:{token:setupToken,password}})).status,403);assert.equal((await call(env,'/api/login',{method:'POST',body:{password:'wrong wrong wrong'}})).status,401);const login=await call(env,'/api/login',{method:'POST',body:{password}});assert.equal(login.status,200);assert.match(login.headers.get('Set-Cookie'),/HttpOnly; Secure; SameSite=Strict/);assert.equal((await call(env,'/api/site',{...auth,method:'POST',body:{version:1,action:'save',document:newDoc()},originHeader:'https://attacker.test'})).status,403);assert.equal((await call(env,'/api/site',{cookie:auth.cookie,method:'POST',body:{version:1,action:'save',document:newDoc()}})).status,403);assert.equal((await call(env,'/api/site',auth)).status,200);});
test('drafts remain private, publish is atomic, stale saves cannot overwrite',async()=>{const env=fixture(),auth=await signIn(env),doc=newDoc();doc.copy.en.title='A private new direction';let r=await call(env,'/api/site',{...auth,method:'POST',body:{document:doc,version:1,action:'save'}});assert.equal(r.status,200);assert.doesNotMatch(await(await call(env,'/')).text(),/A private new direction/);assert.match(await(await call(env,'/preview',auth)).text(),/A private new direction/);r=await call(env,'/api/site',{...auth,method:'POST',body:{document:doc,version:1,action:'publish'}});assert.equal(r.status,409);assert.equal((await call(env,'/api/site',{...auth,method:'POST',body:{document:doc,version:2,action:'publish'}})).status,200);assert.match(await(await call(env,'/')).text(),/A private new direction/);const versions=await(await call(env,'/api/history',auth)).json();assert.deepEqual(versions.map(x=>x.version),[2,1]);});
test('uploads strip metadata, stay private until published, and are protected when referenced',async()=>{const env=fixture(),auth=await signIn(env),bytes=new Uint8Array(readFileSync(new URL('./fixtures/photo.jpg',import.meta.url)));const r=await call(env,'/api/media',{...auth,method:'POST',body:bytes,type:'image/jpeg'});assert.equal(r.status,201);const {url,id}=await r.json();assert.equal((await call(env,url)).status,404);assert.equal((await call(env,url,auth)).status,200);const doc=newDoc();doc.items[0].image=url;doc.items[0].kind='piece';doc.mode='catalogue';doc.whatsapp='923001234567';doc.copy.en.delivery='Delivery agreed in chat before confirmation.';doc.copy.en.returns='Contact us to agree return conditions before ordering.';doc.items[0].price=4500;assert.equal((await call(env,'/api/site',{...auth,method:'POST',body:{document:doc,version:1,action:'publish'}})).status,200);assert.equal((await call(env,url)).status,200);const home=await(await call(env,'/')).text();assert.match(home,/PKR 4,500/);const detail=await(await call(env,'/piece/indigo-stories')).text();assert.match(detail,/https:\/\/wa.me\/923001234567\?text=/);assert.match(detail,/Ask about this piece/);assert.equal((await call(env,'/api/media/delete',{...auth,method:'POST',body:{id}})).status,409);doc.items[0].visible=false;assert.equal((await call(env,'/api/site',{...auth,method:'POST',body:{document:doc,version:2,action:'publish'}})).status,200);assert.equal((await call(env,url)).status,404);assert.equal((await call(env,'/piece/indigo-stories')).status,404);assert.equal((await call(env,'/api/media',{...auth,method:'POST',body:new Uint8Array([1,2,3]),type:'image/jpeg'})).status,400);assert.throws(()=>cleanJpeg(new Uint8Array(300001)));});
test('mode validation, visibility and safe escaped seller content',()=>{let doc=newDoc();assert.deepEqual(validateDocument(doc),doc);doc.mode='enquiries';assert.throws(()=>validateDocument(doc),/WhatsApp/);doc.whatsapp='+92 300 1234567';assert.equal(validateDocument(doc).whatsapp,'923001234567');doc.mode='catalogue';assert.throws(()=>validateDocument(doc),/delivery/);doc=newDoc();doc.items[0].kind='piece';assert.throws(()=>validateDocument(doc),/photograph/);doc=newDoc();doc.whatsapp='923001234567';doc.email='private@example.com';doc.showContact=false;assert.equal(publicDocument(doc).email,'');assert.doesNotMatch(renderPage(doc).html,/private@example.com|wa.me\/923001234567/);doc.copy.en.title='<script>alert(1)</script>';assert.match(renderPage(doc).html,/&lt;script&gt;/);assert.doesNotMatch(renderPage(doc).html,/<script>alert/);doc.items[0].image='javascript:alert(1)';assert.throws(()=>validateDocument(doc));});
test('portfolio and sold-out pieces never expose order buttons',()=>{const doc=newDoc();doc.whatsapp='923001234567';doc.items[0].kind='piece';doc.items[0].image='/media/'+crypto.randomUUID();doc.items[0].price=1000;let page=renderPage(doc,{path:'/piece/indigo-stories'}).html;assert.doesNotMatch(page,/Ask about this piece|PKR 1,000/);doc.mode='enquiries';page=renderPage(doc,{path:'/piece/indigo-stories'}).html;assert.match(page,/Ask about this piece/);assert.doesNotMatch(page,/PKR 1,000/);doc.items[0].status='Sold out';assert.doesNotMatch(renderPage(doc,{path:'/piece/indigo-stories'}).html,/Ask about this piece/);});
test('logout revokes sessions; password changes revoke all sessions',async()=>{const env=fixture(),auth=await signIn(env);let r=await call(env,'/api/password',{...auth,method:'POST',body:{current:password,password:'a different long password'}});assert.equal(r.status,200);assert.equal((await call(env,'/api/site',auth)).status,401);r=await call(env,'/api/login',{method:'POST',body:{password:'a different long password'}});const data=await r.json(),auth2={cookie:r.headers.get('Set-Cookie').split(';')[0],csrf:data.csrf};assert.equal((await call(env,'/api/logout',{...auth2,method:'POST',body:{}})).status,200);assert.equal((await call(env,'/api/site',auth2)).status,401);});
test('oversized payload, missing photo and repeated login abuse are rejected',async()=>{const env=fixture(),auth=await signIn(env);assert.equal((await call(env,'/api/site',{...auth,method:'POST',body:'x'.repeat(450001)})).status,413);const doc=newDoc();doc.items[0].image='/media/'+crypto.randomUUID();assert.equal((await call(env,'/api/site',{...auth,method:'POST',body:{document:doc,version:1,action:'save'}})).status,400);for(let i=0;i<13;i++)await call(env,'/api/login',{method:'POST',body:{password:'bad'}});assert.equal((await call(env,'/api/login',{method:'POST',body:{password}})).status,429);});
