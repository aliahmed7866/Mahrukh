/* Progressive conveniences; live forms remain usable without JavaScript. */
(() => {
 const t=window.MahrukhI18n?.t||((message,values={})=>message.replace(/\{(\w+)\}/g,(match,key)=>values[key]??match));
 const status=document.querySelector('#save-status');
 let statusTimer;
 function announce(message){
  if(!status)return;
  status.querySelector('span').textContent=message;status.hidden=false;
  clearTimeout(statusTimer);statusTimer=setTimeout(()=>{status.hidden=true;},6500);
 }
 function paint(button,saved,name){
  button.setAttribute('aria-pressed',String(saved));
  button.setAttribute('aria-label',saved?t('Remove {name} from saved pieces',{name}):t('Save {name}',{name}));
  button.querySelector('.save-label').textContent=saved?t('Saved'):t('Save');
 }
 function counts(count){document.querySelectorAll('[data-saved-count]').forEach(el=>el.textContent=count);}
 function savedEmpty(){
  const grid=document.querySelector('.saved-grid');if(!grid)return;
  const count=[...grid.querySelectorAll('.product-card')].filter(c=>!c.hidden).length;
  document.querySelector('.saved-empty').hidden=count>0;
  document.querySelector('.saved-toolbar').hidden=count===0;
 }
 document.addEventListener('submit',async e=>{
  const form=e.target;if(!form.matches('[data-save-form]'))return;
  e.preventDefault();const button=form.querySelector('button');button.disabled=true;
  try{
   const response=await fetch(form.action,{method:'POST',body:new FormData(form),headers:{'X-Mahrukh-Saved':'1'}});
   if(!response.ok){
    const page=new DOMParser().parseFromString(await response.text(),'text/html');
    announce(page.querySelector('main .page p:not(.eyebrow)')?.textContent||t('We couldn’t save that change. Please try again.'));return;
   }
   const result=await response.json();
   document.querySelectorAll('[data-save-form]').forEach(other=>{
    if(other.dataset.pieceId!==form.dataset.pieceId)return;
    other.querySelector('[name=action]').value=result.saved?'remove':'save';
    paint(other.querySelector('button'),result.saved,other.dataset.pieceName);
   });
   counts(result.count);
   if(!result.saved&&form.closest('.saved-grid')){
    form.closest('.product-card').hidden=true;savedEmpty();
    document.querySelector('.saved-grid .product-card:not([hidden]) .save-piece, .saved-empty a')?.focus();
   }
   announce(result.saved?t('Saved for another look.'):t('Removed from your saved pieces.'));
  }catch{announce(t('Your connection paused. Reload the page to check your saved pieces.'));}
  finally{button.disabled=false;}
 });
 if(document.body.dataset.designPreview==='true'){
  const valid=new Set((document.body.dataset.demoProductIds||'').split(',').map(Number));
  let saved=[];
  try{const raw=JSON.parse(sessionStorage.getItem('mahrukh-demo-saved')||'[]');if(Array.isArray(raw))saved=[...new Set(raw.filter(id=>Number.isInteger(id)&&valid.has(id)))].slice(0,24);}catch{}
  function render(){
   counts(saved.length);
   document.querySelectorAll('[data-demo-save]').forEach(button=>paint(button,saved.includes(Number(button.dataset.demoSave)),button.dataset.pieceName));
   document.querySelectorAll('.saved-grid .product-card').forEach(card=>card.hidden=!saved.includes(Number(card.dataset.id)));
   savedEmpty();
  }
  function persist(){
   try{sessionStorage.setItem('mahrukh-demo-saved',JSON.stringify(saved));return true;}
   catch{announce(t('Browser storage is unavailable. Your favourites will last only on this page.'));return false;}
  }
  document.addEventListener('click',e=>{
   const button=e.target.closest('[data-demo-save]');
   if(button){
    const id=Number(button.dataset.demoSave);if(!valid.has(id))return;
    const exists=saved.includes(id);saved=exists?saved.filter(x=>x!==id):[...saved,id].slice(0,24);
    const ok=persist();render();if(ok)announce(exists?t('Removed from your saved pieces.'):t('Saved for another look.'));
    if(exists&&button.closest('.saved-grid'))document.querySelector('.saved-grid .product-card:not([hidden]) .save-piece, .saved-empty a')?.focus();
   }
   if(e.target.closest('[data-clear-saved]')){saved=[];persist();render();document.querySelector('.saved-empty a')?.focus();}
  });render();
 }
 const filter=document.querySelector('.filter-drawer');
 if(filter&&matchMedia('(max-width:650px)').matches){
  const params=new URLSearchParams(location.search);
  filter.open=['q','category','occasion','fabric_family','size','budget'].some(k=>params.get(k));
 }
 const main=document.querySelector('#main-product-image'),photo=document.querySelector('#photo-dialog');
 if(main&&photo){
  const thumbnails=[...document.querySelectorAll('.thumbnail[data-image]')];
  const images=thumbnails.length?thumbnails.map(b=>b.dataset.image):[main.getAttribute('src')];
  const launcher=document.querySelector('[data-open-gallery]');let current=0,opener;
  function show(index){
   current=(index+images.length)%images.length;main.src=images[current];launcher.href=images[current];
   photo.querySelector('[data-large-photo]').src=images[current];
   photo.querySelector('[data-photo-count]').textContent=t('Photo {current} of {total}',{current:current+1,total:images.length});
   thumbnails.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===current)));
  }
  thumbnails.forEach((b,i)=>b.addEventListener('click',()=>show(i)));
  launcher.addEventListener('click',e=>{e.preventDefault();opener=document.activeElement;show(current);photo.showModal();document.body.classList.add('drawer-open');});
  photo.querySelector('[data-close-photo]').addEventListener('click',()=>photo.close());
  photo.querySelector('[data-photo-prev]').addEventListener('click',()=>show(current-1));
  photo.querySelector('[data-photo-next]').addEventListener('click',()=>show(current+1));
  photo.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();const direction=document.documentElement.dir==='rtl'?-1:1;show(current+(e.key==='ArrowLeft'?-1:1)*direction);}});
  photo.addEventListener('close',()=>{document.body.classList.remove('drawer-open');opener?.focus();});
 }
 function chooseSize(input){
  const size=input.value;
  document.querySelectorAll('[data-measure-size]').forEach(row=>{row.classList.toggle('chosen-measurement',row.dataset.measureSize===size);});
  document.querySelectorAll('[data-piece-question]').forEach(link=>{const url=new URL(link.href);url.searchParams.set('size',size);link.href=url.href;});
  const feedback=document.querySelector('[data-size-feedback]'),quantity=document.querySelector('#quantity');
  if(feedback&&input.dataset.stock!==undefined){
   const stock=Number(input.dataset.stock),max=Math.min(stock,10);
   feedback.textContent=t('Size {size} selected · {stock} available.',{size,stock});
   if(quantity){quantity.max=String(max);if(Number(quantity.value)>max)quantity.value=String(max);}
   const label=document.querySelector('[data-add-label]');if(label)label.textContent=t('Add {size} to bag',{size});
  }
 }
 document.querySelectorAll('[name=size],[name=demo-size]').forEach(input=>{input.addEventListener('change',()=>chooseSize(input));if(input.checked)chooseSize(input);});
})();
