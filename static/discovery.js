(() => {
 document.querySelectorAll('[data-measure-unit]').forEach(button => button.addEventListener('click', () => {
  const section=button.closest('.size-guide'), metric=button.dataset.measureUnit==='cm';
  section.querySelectorAll('[data-inches]').forEach(cell => { const value=Number(cell.dataset.inches); if(Number.isFinite(value)) cell.textContent=Number((value*(metric?2.54:1)).toFixed(2)).toString(); });
  section.querySelector('[data-measure-caption]').textContent=window.MahrukhPreview?.t(metric?'centimetres':'inches')||(metric?'centimetres':'inches');
  section.querySelectorAll('[data-measure-unit]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
 }));
})();
