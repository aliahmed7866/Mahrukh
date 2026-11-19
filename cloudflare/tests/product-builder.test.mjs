import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyProduct,chooseType,validateProduct,buildDescription,GARMENTS,productCategory} from '../public/product-builder.mjs';
import {defaults,validateDocument} from '../content.mjs';
import {renderPage} from '../render.mjs';
const product=(group,type,extra={})=>({...chooseType({...emptyProduct(),group},type),...extra});
test('suit presets distinguish garments and count only included pieces',()=>{
 let p=product('sets','shalwar-kameez',{stitching:'ready',fabric:'lawn',colour:'emerald',work:'embroidered',sizes:['S','M']});
 let copy=buildDescription(p);assert.match(copy.summary,/2-piece set: Kameez \/ shirt and Shalwar/);assert.doesNotMatch(copy.story,/dupatta|100%|handmade|cotton/i);assert.ok(copy.story.includes('\n\nFabric: Lawn.'));assert.ok(!copy.story.includes('\\n'));
 p.components.push('dupatta');copy=buildDescription(p);assert.match(copy.includes,/3-piece set/);assert.match(copy.includes,/Dupatta/);assert.equal(copy.sizes,'S, M');
 const kp=buildDescription(product('sets','kurta-pajama'));assert.match(kp.includes,/Kurta and Pajama/);assert.doesNotMatch(kp.includes,/shalwar/i);
});
test('standalone upperwear and lowerwear never promise a complete outfit',()=>{
 for(const [group,type] of [['upperwear','kurta'],['lowerwear','pajama'],['lowerwear','gharara'],['lowerwear','sharara']]){
  const p=product(group,type);const copy=buildDescription(p);assert.match(copy.summary,/only/);assert.match(copy.includes,/Other pictured pieces are not included/);assert.doesNotMatch(copy.summary,/piece set/);assert.equal(productCategory(p),group==='upperwear'?'Upperwear / tops':'Lowerwear / bottoms');
 }
});
test('unstitched descriptions omit sewn sizing and do not invent fibre composition or care',()=>{
 const p=product('sets','shirt-trousers',{stitching:'unstitched',fabric:'lawn',fit:'slim',sleeves:'full',sizes:['S'],customSizes:'34',measurements:'Shirt 3 m; trousers 2.5 m.'});
 const copy=buildDescription(p);assert.equal(copy.sizes,'');assert.equal(copy.care,'');assert.match(copy.title,/fabric$/);assert.match(copy.story,/Supplied as fabric; stitching is not included/);assert.match(copy.includes,/shirt fabric/);assert.match(copy.story,/Shirt 3 m/);assert.doesNotMatch(copy.story,/Slim fit|Full sleeves|Available sizes|100%|Cotton/);
});
test('all garment presets are valid; mismatched groups, missing parts and invalid choices fail',()=>{
 for(const t of GARMENTS){const p=product(t.group,t.value,{customType:t.value.endsWith('-other')?'Custom garment':''});assert.doesNotThrow(()=>validateProduct(p),t.value);}
 assert.throws(()=>validateProduct(product('sets','kurta-pajama',{components:['kurta']})),/named garments/);
 assert.throws(()=>validateProduct(product('upperwear','kurta',{components:['kurta','pajama']})),/Standalone/);
 assert.throws(()=>validateProduct(product('upperwear','kurta',{group:'lowerwear'})),/selected product group/);
 assert.throws(()=>validateProduct({...emptyProduct(),fabric:'made-up'}),/fabric/);
 assert.throws(()=>validateProduct({...emptyProduct(),sizes:['S','S']}),/sizes/);
 assert.equal(buildDescription(emptyProduct()),null);
});
test('legacy entries stay unchanged and builder details round-trip through validation and rendering',()=>{
 assert.deepEqual(validateDocument(structuredClone(defaults)),defaults);
 const doc=structuredClone(defaults),p=product('lowerwear','pajama',{audience:'men',stitching:'ready',fabric:'cotton',colour:'white'});
 doc.items.push({...defaults.items[0],...buildDescription(p),id:'pajama',kind:'piece',image:'/media/'+crypto.randomUUID(),product:p});
 const saved=validateDocument(doc);assert.deepEqual(saved.items.at(-1).product,p);
 const home=renderPage(saved).html;assert.match(home,/data-category="Lowerwear \/ bottoms"/);assert.match(home,/Pajama \/ pyjama/);
 const detail=renderPage(saved,{path:'/piece/pajama'}).html;assert.match(detail,/<dt>Garment<\/dt><dd>Pajama \/ pyjama/);assert.match(detail,/<dt>For<\/dt><dd>Men/);
 assert.match(renderPage(saved,{lang:'ur'}).html,/شلوار اور پاجامے/);
});
test('custom description inputs are escaped on public pages',()=>{
 const doc=structuredClone(defaults),p=product('upperwear','upperwear-other',{customType:'<script>alert(1)</script>',colour:'other',colourNotes:'<img src=x onerror=alert(1)>'});
 const piece={...defaults.items[0],...buildDescription(p),id:'custom',kind:'piece',image:'/media/'+crypto.randomUUID(),product:p};doc.items.push(piece);
 const html=renderPage(validateDocument(doc),{path:'/piece/custom'}).html;assert.match(html,/&lt;script&gt;/);assert.doesNotMatch(html,/<script>alert|<img src=x/);
});
