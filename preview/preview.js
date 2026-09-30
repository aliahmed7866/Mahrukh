(() => {
 const grid=document.querySelector('.product-grid');
 if(grid){
  const cards=[...grid.querySelectorAll('.product-card')];
  const params=new URLSearchParams(location.search);
  const query=params.get('q')||'';
  const category=params.get('category')||'';
  const sort=params.get('sort')||'featured';
  const search=document.querySelector('#search');search.value=query;
  const form=document.querySelector('.sort-form');
  form.querySelector('[name=q]').value=query;
  form.querySelector('[name=category]').value=category;
  document.querySelector('#sort').value=['featured','price-low','price-high'].includes(sort)?sort:'featured';
  let count=0;
  for(const card of cards){
   const matches=(!category||card.dataset.category===category)&&card.dataset.name.toLowerCase().includes(query.toLowerCase());
   card.hidden=!matches;if(matches)count++;
  }
  if(sort==='price-low'||sort==='price-high')cards.sort((a,b)=>(Number(a.dataset.price)-Number(b.dataset.price))*(sort==='price-low'?1:-1)).forEach(card=>grid.append(card));
  document.querySelector('#result-count').textContent=count;
  document.querySelector('#collection-title').textContent=category||(query?'Search results':'The sample collection');
  document.querySelector('#no-results').hidden=count!==0;
  document.querySelectorAll('.main-nav a').forEach(a=>{if((new URL(a.href).searchParams.get('category')||'')===category)a.setAttribute('aria-current','page');});
  if(query||category)document.querySelector('#collection').scrollIntoView({behavior:'instant'});
 }
 document.querySelectorAll('[name=demo-size]').forEach(input=>input.addEventListener('change',()=>{document.querySelector('#size-preview').textContent='Previewing size: '+input.value;}));
})();

(() => {
 const cart=document.querySelector('#demo-cart'),help=document.querySelector('#demo-help');
 let opener,items=[];
 try{const stored=JSON.parse(sessionStorage.getItem('mahrukh-demo-bag')||'[]');if(Array.isArray(stored))items=stored.filter(x=>Number.isFinite(x.price)&&Number.isInteger(x.quantity)&&x.quantity>0&&x.quantity<=10&&typeof x.name==='string'&&typeof x.size==='string').slice(0,20);}catch{}
 const money=n=>'PKR '+n.toLocaleString('en-PK');
 function save(){try{sessionStorage.setItem('mahrukh-demo-bag',JSON.stringify(items));}catch{} render();}
 function element(tag,text,cls){const e=document.createElement(tag);if(text)e.textContent=text;if(cls)e.className=cls;return e;}
 function render(){
  document.querySelectorAll('[data-cart-count]').forEach(el=>{el.textContent=items.reduce((n,x)=>n+x.quantity,0);el.closest('button')?.setAttribute('aria-label','Preview shopping cart, '+el.textContent+' sample items');});
  const container=document.querySelector('#demo-cart-lines');container.replaceChildren();
  if(!items.length){const empty=element('div','','empty');empty.append(element('h3','Your next favourite awaits.'),element('p','Explore a sample piece and try adding a size to see the bag design.'));container.append(empty);}
  items.forEach((item,i)=>{const row=element('article','','demo-bag-line');const details=element('div');details.append(element('h3',item.name),element('p',item.size+' · Qty '+item.quantity,'muted'),element('strong',money(item.price*item.quantity)));const remove=element('button','Remove','text-button');remove.type='button';remove.setAttribute('aria-label','Remove '+item.name+' size '+item.size);remove.addEventListener('click',()=>{items.splice(i,1);save();cart.querySelector('button')?.focus();});row.append(details,remove);container.append(row);});
  if(items.length){const total=element('div','','cart-total');total.append(element('span','Illustrative subtotal'),element('strong',money(items.reduce((n,x)=>n+x.price*x.quantity,0))));container.append(total);}
 }
 function open(d){opener=document.activeElement;d.showModal();document.body.classList.add('drawer-open');}
 [cart,help].forEach(d=>d.addEventListener('close',()=>{document.body.classList.remove('drawer-open');opener?.focus();}));
 document.addEventListener('click',e=>{
  if(e.target.closest('[data-demo-cart]')){render();open(cart);}
  if(e.target.closest('[data-demo-help]'))open(help);
  if(e.target.closest('[data-demo-close]'))e.target.closest('dialog').close();
  const add=e.target.closest('[data-demo-add]');
  if(add){const size=document.querySelector('[name=demo-size]:checked')?.value||'Sample';const found=items.find(x=>x.id===add.dataset.id&&x.size===size);if(found){found.quantity=Math.min(found.quantity+1,10);}else if(items.length<20){items.push({id:add.dataset.id,name:add.dataset.name,size,price:Number(add.dataset.price),quantity:1});}save();open(cart);}
 });render();
})();
