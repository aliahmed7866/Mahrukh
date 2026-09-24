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
