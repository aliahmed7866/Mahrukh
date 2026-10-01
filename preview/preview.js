(() => {
 const t=window.MahrukhI18n.t;
 const grid=document.querySelector('#catalog-grid');
 if(grid){
  const cards=[...grid.querySelectorAll('.product-card')];
  const params=new URLSearchParams(location.search);
  const form=document.querySelector('.catalog-filters');
  const chosen={};
  for(const name of ['category','occasion','fabric_family','size','sort']){
   const select=form.querySelector('[name="'+name+'"]');
   const value=params.get(name)||'';
   chosen[name]=[...select.options].some(o=>o.value===value)?value:(name==='sort'?'featured':'');
   select.value=chosen[name];
  }
  const query=(params.get('q')||'').trim().slice(0,100);
  const rawBudget=params.get('budget')||'';
  const validBudget=!rawBudget||(/^\d{1,8}$/.test(rawBudget)&&Number(rawBudget)>=1&&Number(rawBudget)<=10000000);
  document.querySelector('#search').value=query;
  form.querySelector('[name=q]').value=query;
  form.querySelector('[name=budget]').value=validBudget?rawBudget:'';
  const {category,occasion,fabric_family,size,sort}=chosen;
  let count=0;
  for(const card of cards){
   const matches=validBudget&&(!category||card.dataset.category===category)&&card.dataset.name.toLowerCase().includes(query.toLowerCase())&&(!occasion||card.dataset.occasions.split('|').includes(occasion))&&(!fabric_family||card.dataset.fabric===fabric_family)&&(!size||card.dataset.sizes.split('|').includes(size))&&(!rawBudget||Number(card.dataset.price)<=Number(rawBudget));
   card.hidden=!matches;if(matches)count++;
  }
  if(sort==='price-low'||sort==='price-high')cards.sort((a,b)=>(Number(a.dataset.price)-Number(b.dataset.price))*(sort==='price-low'?1:-1)).forEach(card=>grid.append(card));
  document.querySelector('#result-count').textContent=count;
  document.querySelector('#result-noun').textContent=t(count===1?'sample piece':'sample pieces');
  const chips=document.querySelector('.active-filters');chips.replaceChildren();
  for(const name of ['q','category','occasion','fabric_family','size','budget']){
   const value=name==='q'?query:name==='budget'?(validBudget?rawBudget:''):chosen[name];if(!value)continue;
   const option=form.querySelector('[name="'+name+'"] option:checked');
   const label=name==='budget'?t('Up to PKR {amount}',{amount:Number(value).toLocaleString('en-PK')}):option?option.textContent:value;
   const url=new URL(location.href);url.searchParams.delete(name);url.hash='collection';
   const link=document.createElement('a');link.href=url.href;link.textContent=label+' ×';link.setAttribute('aria-label',t('Remove filter {label}',{label}));chips.append(link);
  }
  chips.hidden=chips.children.length===0;
  document.querySelector('#collection-title').textContent=category?t(category):t(query?'Search results':'The sample collection');
  const empty=document.querySelector('#no-results');empty.hidden=count!==0;
  if(!validBudget)empty.querySelector('p').textContent=t('Enter a maximum price from PKR 1 to 10,000,000.');
  document.querySelectorAll('.main-nav a').forEach(a=>{if((new URL(a.href).searchParams.get('category')||'')===category)a.setAttribute('aria-current','page');});
  if(query||category||occasion||fabric_family||size||rawBudget){
   document.querySelectorAll('.hero,.values,.category-section').forEach(el=>el.hidden=true);
   document.querySelector('#collection').scrollIntoView({behavior:'instant'});
  }
 }
 const selectedDemoSize=document.querySelector('[name=demo-size]:checked');
 if(selectedDemoSize)document.querySelector('#size-preview').textContent=t('Previewing size: {size}',{size:selectedDemoSize.value});
 document.querySelectorAll('[name=demo-size]').forEach(input=>input.addEventListener('change',()=>{document.querySelector('#size-preview').textContent=t('Previewing size: {size}',{size:input.value});}));
})();

(() => {
 const t=window.MahrukhI18n.t;
 const cart=document.querySelector('#demo-cart'),help=document.querySelector('#demo-help');
 let opener,items=[];
 try{const stored=JSON.parse(sessionStorage.getItem('mahrukh-demo-bag')||'[]');if(Array.isArray(stored))items=stored.filter(x=>Number.isFinite(x.price)&&Number.isInteger(x.quantity)&&x.quantity>0&&x.quantity<=10&&typeof x.name==='string'&&typeof x.size==='string').slice(0,20);}catch{}
 const money=n=>'PKR '+n.toLocaleString('en-PK');
 function save(){try{sessionStorage.setItem('mahrukh-demo-bag',JSON.stringify(items));}catch{} render();}
 function element(tag,text,cls){const e=document.createElement(tag);if(text)e.textContent=text;if(cls)e.className=cls;return e;}
 function render(){
  document.querySelectorAll('[data-cart-count]').forEach(el=>{el.textContent=items.reduce((n,x)=>n+x.quantity,0);el.closest('button')?.setAttribute('aria-label',t('Preview shopping cart, {count} sample items',{count:el.textContent}));});
  const container=document.querySelector('#demo-cart-lines');container.replaceChildren();
  if(!items.length){const empty=element('div','','empty');empty.append(element('h3',t('Your next favourite awaits.')),element('p',t('Explore a sample piece and try adding a size to see the bag design.')));container.append(empty);}
  items.forEach((item,i)=>{const row=element('article','','demo-bag-line');const details=element('div');details.append(element('h3',t(item.name)),element('p',t('{size} · Qty {quantity}',{size:item.size,quantity:item.quantity}),'muted'),element('strong',money(item.price*item.quantity)));const remove=element('button',t('Remove'),'text-button');remove.type='button';remove.setAttribute('aria-label',t('Remove {name} size {size}',{name:t(item.name),size:item.size}));remove.addEventListener('click',()=>{items.splice(i,1);save();cart.querySelector('button')?.focus();});row.append(details,remove);container.append(row);});
  if(items.length){const total=element('div','','cart-total');total.append(element('span',t('Illustrative subtotal')),element('strong',money(items.reduce((n,x)=>n+x.price*x.quantity,0))));container.append(total);}
 }
 function open(d){opener=document.activeElement;d.showModal();document.body.classList.add('drawer-open');}
 [cart,help].forEach(d=>d.addEventListener('close',()=>{document.body.classList.remove('drawer-open');opener?.focus();}));
 document.addEventListener('click',e=>{
  if(e.target.closest('[data-demo-cart]')){render();open(cart);}
  const question=e.target.closest('[data-demo-help]');
  if(question){const text=help.querySelector('[data-demo-question]');text.hidden=!question.dataset.question;if(question.dataset.question)text.textContent=question.dataset.productName+' · '+(document.querySelector('[name=demo-size]:checked')?.value||t('Size not selected'))+' — '+question.dataset.question;open(help);}
  if(e.target.closest('[data-demo-close]'))e.target.closest('dialog').close();
  const add=e.target.closest('[data-demo-add]');
  if(add){const size=document.querySelector('[name=demo-size]:checked')?.value||'Sample';const found=items.find(x=>x.id===add.dataset.id&&x.size===size);if(found){found.quantity=Math.min(found.quantity+1,10);}else if(items.length<20){items.push({id:add.dataset.id,name:add.dataset.name,size,price:Number(add.dataset.price),quantity:1});}save();open(cart);}
 });render();
})();
