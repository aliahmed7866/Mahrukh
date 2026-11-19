// Shared by the studio and server. Terminology sources: ../PRODUCT-CATEGORIES.md.
const options=(rows)=>rows.map(([value,label,ur])=>({value,label,ur:ur||label}));
export const GROUPS=options([
 ['sets','Suits & sets','سوٹ اور سیٹ'],['upperwear','Upperwear / tops','قمیض اور کرتے'],
 ['lowerwear','Lowerwear / bottoms','شلوار اور پاجامے'],['layers','Waistcoats & outerwear','واسکٹ اور شیروانی'],['accessories','Dupattas & shawls','دوپٹے اور شالیں']
]);
const types=(group,rows)=>rows.map(([value,label,ur,parts])=>({value,label,ur,group,parts:parts||[value]}));
export const GARMENTS=[
 ...types('sets',[
 ['shalwar-kameez','Shalwar kameez suit','شلوار قمیض',['kameez','shalwar']],
 ['kurta-pajama','Kurta pajama set','کرتا پاجامہ',['kurta','pajama']],
 ['kurta-shalwar','Kurta shalwar set','کرتا شلوار',['kurta','shalwar']],
 ['kurta-trousers','Kurta & trousers','کرتا اور ٹراؤزر',['kurta','trousers']],
 ['shirt-trousers','Kameez / shirt & trousers','قمیض اور ٹراؤزر',['kameez','trousers']],
 ['shirt-dupatta','Kameez / shirt & dupatta','قمیض اور دوپٹہ',['kameez','dupatta']],
 ['gharara-suit','Gharara suit','غرارہ سوٹ',['kameez','gharara']],
 ['sharara-suit','Sharara suit','شرارہ سوٹ',['kameez','sharara']],
 ['lehenga-choli','Lehenga choli set','لہنگا چولی',['choli','lehenga']],
 ['pishwas-suit','Pishwas & trousers','پشواز اور ٹراؤزر',['pishwas','trousers']],
 ['anarkali-suit','Anarkali & trousers','انارکلی اور ٹراؤزر',['anarkali','trousers']],
 ['angarkha-suit','Angarkha & trousers','انگرکھا اور ٹراؤزر',['angarkha','trousers']]
 ]),
 ...types('upperwear',[
 ['kurta','Kurta','کرتا'],['kameez','Kameez / shirt','قمیض'],['kurti','Kurti','کرتی'],['angarkha','Angarkha','انگرکھا'],
 ['anarkali','Anarkali','انارکلی'],['pishwas','Pishwas','پشواز'],['choli','Choli / blouse','چولی']
 ]),
 ...types('lowerwear',[
 ['shalwar','Shalwar','شلوار'],['farshi-shalwar','Farshi shalwar','فرشی شلوار'],['pajama','Pajama / pyjama','پاجامہ'],
 ['churidar','Churidar','چوڑی دار پاجامہ'],['trousers','Straight trousers','سیدھے ٹراؤزر'],['cigarette-pants','Cigarette trousers','سگریٹ پینٹ'],
 ['palazzo','Palazzo trousers','پلازو'],['culottes','Culottes','کیولٹس'],['gharara','Gharara','غرارہ'],['sharara','Sharara','شرارہ'],['lehenga','Lehenga / skirt','لہنگا']
 ]),
 ...types('layers',[['waistcoat','Waistcoat / koti','واسکٹ'],['sherwani','Sherwani','شیروانی'],['achkan','Achkan','اچکن']]),
 ...types('accessories',[['dupatta','Dupatta','دوپٹہ'],['shawl','Shawl / chadar','شال'],['stole','Stole','اسٹول']]),
 ...GROUPS.map(g=>({value:g.value+'-other',label:'Other / custom '+(g.value==='sets'?'set':'piece'),ur:'دیگر',group:g.value,parts:[]}))
];
export const PARTS=GARMENTS.filter(x=>x.group!=='sets'&&!x.value.endsWith('-other')).map(({value,label,ur})=>({value,label,ur}));
export const OPTIONS={
 audience:options([['women','Women','خواتین'],['men','Men','مرد'],['girls','Girls','بچیاں'],['boys','Boys','بچے'],['unisex','Unisex','سب کے لیے']]),
 stitching:options([['ready','Ready to wear / stitched','سلا ہوا'],['unstitched','Unstitched fabric','بغیر سلا'],['made-to-order','Made to order','آرڈر پر تیار']]),
 fabric:options([['lawn','Lawn'],['cotton','Cotton'],['cambric','Cambric'],['khaddar','Khaddar'],['linen','Linen'],['karandi','Karandi'],['wash-wear','Wash & wear'],['viscose','Viscose / rayon'],['chiffon','Chiffon'],['organza','Organza'],['georgette','Georgette'],['silk','Silk'],['raw-silk','Raw silk'],['satin','Satin'],['velvet','Velvet'],['jacquard','Jacquard'],['dobby','Dobby'],['net','Net'],['voile','Voile'],['blend','Blend'],['other','Other / mixed fabrics']]),
 colour:options([['black','Black'],['white','White'],['ivory','Ivory'],['beige','Beige'],['brown','Brown'],['blue','Blue'],['navy','Navy'],['teal','Teal'],['green','Green'],['emerald','Emerald'],['mint','Mint'],['red','Red'],['maroon','Maroon'],['pink','Pink'],['rose','Rose'],['peach','Peach'],['purple','Purple'],['yellow','Yellow'],['mustard','Mustard'],['orange','Orange'],['grey','Grey'],['gold','Gold'],['silver','Silver'],['multicolour','Multicolour'],['other','Other colour']]),
 work:options([['plain','Plain'],['printed','Printed'],['embroidered','Embroidered'],['printed-embroidered','Printed & embroidered'],['block-print','Block printed'],['woven','Woven pattern'],['textured','Textured'],['embellished','Embellished'],['lace','Lace detailing']]),
 occasion:options([['everyday','Everyday wear'],['work','Work / office'],['eid','Eid'],['festive','Festive occasions'],['mehndi','Mehndi'],['wedding','Wedding guest'],['formal','Formal occasions'],['bridal','Bridal']]),
 fit:options([['regular','Regular fit'],['relaxed','Relaxed fit'],['slim','Slim fit'],['loose','Loose fit'],['a-line','A-line'],['flared','Flared']]),
 sleeves:options([['full','Full sleeves'],['three-quarter','Three-quarter sleeves'],['half','Half sleeves'],['sleeveless','Sleeveless']]),
 neckline:options([['round','Round neckline'],['v-neck','V-neckline'],['band','Band / mandarin collar'],['shirt','Shirt collar'],['boat','Boat neckline'],['square','Square neckline']]),
 length:options([['short','Short length'],['knee','Knee length'],['calf','Calf length'],['ankle','Ankle length'],['floor','Floor length']]),
 care:options([['label','Follow the garment care label.'],['hand-wash','Gentle hand wash separately in cold water.'],['machine','Gentle machine wash according to the care label.'],['dry-clean','Dry clean only.']])
};
export const SIZES=['XS','S','M','L','XL','XXL','XXXL','One size','Made to measure'];
export const emptyProduct=()=>({group:'',type:'',audience:'',stitching:'',fabric:'',fabricNotes:'',colour:'',colourNotes:'',work:'',occasion:'',fit:'',sleeves:'',neckline:'',length:'',care:'',customType:'',components:[],sizes:[],customSizes:'',measurements:''});
export const label=(list,value,lang='en')=>{const o=list.find(x=>x.value===value);return o?(lang==='ur'?o.ur:o.label):'';};
export const garmentTypes=group=>GARMENTS.filter(x=>x.group===group);
export function chooseType(product,value){
 const type=GARMENTS.find(x=>x.value===value&&x.group===product.group);
 return {...product,type:type?.value||'',customType:'',components:[...(type?.parts||[])],...(['lowerwear','accessories'].includes(product.group)?{sleeves:'',neckline:''}:{})};
}
export function validateProduct(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))throw Error('Choose valid product details.');
 const p=emptyProduct(),check=(ok,message)=>{if(!ok)throw Error(message);};
 for(const [key,list] of Object.entries({group:GROUPS,type:GARMENTS,...OPTIONS})){
  const value=raw[key]??'';check(typeof value==='string'&&(!value||list.some(x=>x.value===value)),`Choose a valid ${key}.`);p[key]=value;
 }
 for(const [key,max] of Object.entries({customType:60,fabricNotes:160,colourNotes:60,customSizes:100,measurements:400})){
  const value=raw[key]??'';check(typeof value==='string'&&value.length<=max,`Keep ${key} within ${max} characters.`);p[key]=value.trim();
 }
 for(const [key,allowed] of [['components',PARTS.map(x=>x.value)],['sizes',SIZES]]){
  const value=raw[key]??[];check(Array.isArray(value)&&value.length<=allowed.length&&new Set(value).size===value.length&&value.every(x=>allowed.includes(x)),`Choose valid ${key}.`);p[key]=[...value];
 }
 const type=GARMENTS.find(x=>x.value===p.type);
 check(!p.type||type.group===p.group,'Choose a garment in the selected product group.');
 if(type){check(type.parts.every(x=>p.components.includes(x)),'Keep the named garments in the set, or choose a custom set.');if(p.group!=='sets')check(p.components.length===type.parts.length,'Standalone pieces cannot include a suit. Choose Suits & sets instead.');}
 else check(p.components.length===0,'Choose a garment before adding included pieces.');
 if(p.stitching==='unstitched'){p.sizes=[];p.customSizes='';p.fit='';p.sleeves='';p.neckline='';p.length='';}
 if(['lowerwear','accessories'].includes(p.group)){p.sleeves='';p.neckline='';}
 return p;
}
export function productCategory(p,lang='en'){return label(GROUPS,p?.group,lang);}
export function productFacts(p,lang='en'){
 if(!p?.type)return [];
 const names=lang==='ur'?['لباس','تیاری','کس کے لیے','رنگ','کام','موقع']:['Garment','Finish','For','Colour','Detail','Occasion'];
 const values=[p.customType||label(GARMENTS,p.type,lang),label(OPTIONS.stitching,p.stitching,lang),label(OPTIONS.audience,p.audience,lang),p.colourNotes||label(OPTIONS.colour,p.colour,lang),label(OPTIONS.work,p.work,lang),label(OPTIONS.occasion,p.occasion,lang)];
 return names.map((name,i)=>[name,values[i]]).filter(x=>x[1]);
}
const join=values=>values.length<2?values[0]||'':values.slice(0,-1).join(', ')+' and '+values.at(-1);
export function buildDescription(raw){
 const p=validateProduct(raw),type=GARMENTS.find(x=>x.value===p.type);
 if(!type||p.type.endsWith('-other')&&!p.customType)return null;
 const name=p.customType||type.label,unstitched=p.stitching==='unstitched';
 const colour=p.colourNotes||(p.colour==='other'?'':label(OPTIONS.colour,p.colour));
 const fabric=p.fabricNotes||(p.fabric==='other'?'':label(OPTIONS.fabric,p.fabric));
 const parts=p.components.map(x=>label(PARTS,x));
 const included=parts.length?join(parts.map(x=>unstitched?x.toLowerCase()+' fabric':x)):'';
 const sizes=unstitched?'':[...p.sizes,p.customSizes].filter(Boolean).join(', ');
 const title=[colour,label(OPTIONS.work,p.work),name,unstitched?'fabric':''].filter(Boolean).join(' ').slice(0,100);
 const summary=[`${name}${colour?' in '+colour.toLowerCase():''}${unstitched?' — unstitched fabric':''}.`,p.stitching&&!unstitched?label(OPTIONS.stitching,p.stitching)+'.':'',p.group==='sets'&&parts.length?`${parts.length}-piece set: ${included}.`:included?`Includes ${included.toLowerCase()} only.`:''].filter(Boolean).join(' ').slice(0,400);
 const lines=[summary,fabric?'Fabric: '+fabric+'.':'',label(OPTIONS.work,p.work)?'Detail: '+label(OPTIONS.work,p.work)+'.':'',p.audience?'For: '+label(OPTIONS.audience,p.audience)+'.':'',p.occasion?'Occasion: '+label(OPTIONS.occasion,p.occasion)+'.':'',!unstitched?['fit','sleeves','neckline','length'].map(k=>label(OPTIONS[k],p[k])).filter(Boolean).join(' · '):'',sizes?'Available sizes: '+sizes+'.':'',p.measurements?'Measurements / fabric lengths: '+p.measurements:'',unstitched?'Supplied as fabric; stitching is not included.':''];
 return {title,summary,story:lines.filter(Boolean).join('\n\n'),category:productCategory(p),includes:included?(p.group==='sets'?`${parts.length}-piece set: `:'')+included+(p.group==='sets'?'':'. Other pictured pieces are not included.'):'',fabric,sizes,care:label(OPTIONS.care,p.care)};
}
