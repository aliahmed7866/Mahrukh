/* Static demo only. Store only language; size/filter continuity stays in the URL. */
(() => {
 const ur=document.documentElement.lang==='ur';
 const dictionary=window.MAHRUKH_UR||{};
 const t=(message,values={})=>Object.entries(values).reduce((text,[key,value])=>text.replaceAll('{'+key+'}',value),ur?(dictionary[message]||message):message);
 window.MahrukhPreview={t,ur};
 const current=new URL(location.href),choice=current.searchParams.get('lang');
 let preference;try{preference=localStorage.getItem('mahrukh-demo-language');if(choice==='en'||choice==='ur')localStorage.setItem('mahrukh-demo-language',choice);}catch{}
 function variant(url,lang){url.pathname=url.pathname.replace(/(?:\.ur)?\.html$/,'.html');if(url.pathname.endsWith('/'))url.pathname+='index.html';if(lang==='ur')url.pathname=url.pathname.replace(/\.html$/,'.ur.html');return url;}
 if(!choice&&!ur&&preference==='ur'){location.replace(variant(current,'ur').href);return;}
 const sizeInputs=[...document.querySelectorAll('[name=demo-size]')];
 const selected=sizeInputs.find(input=>input.value===current.searchParams.get('size'));
 if(selected)selected.checked=true;
 function sizeUpdate(){const value=sizeInputs.find(input=>input.checked)?.value;if(!value)return;document.querySelector('#size-preview').textContent=t('Previewing size: {size}',{size:t(value)});const url=new URL(location.href);url.searchParams.set('size',value);history.replaceState(null,'',url);}
 sizeInputs.forEach(input=>input.addEventListener('change',sizeUpdate));if(sizeInputs.length)sizeUpdate();
 document.querySelectorAll('[data-language]').forEach(link=>{
  function update(){const url=variant(new URL(location.href),link.dataset.language);url.searchParams.set('lang',link.dataset.language);url.searchParams.delete('panel');if(document.querySelector('#demo-cart[open]'))url.searchParams.set('panel','bag');link.href=url.href;}
  update();link.addEventListener('click',()=>{update();try{localStorage.setItem('mahrukh-demo-language',link.dataset.language);}catch{}});
 });
 // Explicit links prevent preference redirects after back navigation or storage failure.
 document.querySelectorAll('form.search,.catalog-filters').forEach(form=>{const input=document.createElement('input');input.type='hidden';input.name='lang';input.value=ur?'ur':'en';form.append(input);});
 window.addEventListener('pageshow',()=>{if(new URL(location.href).searchParams.get('panel')==='bag')document.querySelector('[data-demo-cart]')?.click();});
})();
