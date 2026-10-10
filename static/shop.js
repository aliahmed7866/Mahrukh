(() => {
  const t = window.MahrukhI18n?.t || ((message, values = {}) => message.replace(/\{(\w+)\}/g, (match, key) => values[key] ?? match));
  const drawer = document.querySelector('#cart-drawer');
  const body = document.querySelector('#cart-body');
  let opener;
  let cartPending = false;
  let drawerVersion = 0;
  let drawerRead = null;
  const pageCart = document.querySelector('#cart-page-contents');
  document.querySelector('[data-checkout-errors]')?.focus();
  const toast = message => {
    const el = document.querySelector('#toast');
    el.textContent = message; el.hidden = false;
    clearTimeout(el.timer); el.timer = setTimeout(() => { el.hidden = true; }, 4500);
  };
  function replaceCartContents(region, html) {
    // Capture just before replacement so typing during the request is retained.
    // Keep this draft in the DOM only, never cookies or browser storage.
    const oldForm = region.querySelector('[data-checkout-form]');
    const fields = ['name', 'contact', 'city', 'address'];
    const values = Object.fromEntries(fields.map(name => [name, oldForm?.querySelector(`[name="${name}"]`)?.value || '']));
    const payment = oldForm?.querySelector('[name="payment_method"]:checked')?.value;
    region.innerHTML = html;
    const newForm = region.querySelector('[data-checkout-form]');
    if (!newForm || !oldForm) return;
    fields.forEach(name => {
      const field = newForm.querySelector(`[name="${name}"]`);
      if (field) field.value = values[name];
    });
    newForm.querySelectorAll('[name="payment_method"]').forEach(field => {
      field.checked = field.value === payment && !field.disabled;
    });
    // The response owns fresh CSRF/quote/order tokens. Do not copy consent:
    // the shopper must review the new total before placing the order.
    if (Object.values(values).some(Boolean) || payment) {
      newForm.dataset.checkoutRecovered = 'true';
      const notice = document.createElement('p');
      notice.className = 'notice';
      notice.textContent = t('Your delivery details are kept here. Review the updated total and accept the terms again.');
      newForm.prepend(notice);
    }
  }
  function openDrawer() {
    if (!drawer.open) { opener = document.activeElement; drawer.showModal(); document.body.classList.add('drawer-open'); }
  }
  function closeDrawer() { drawer.close(); }
  drawer.addEventListener('close', () => { drawerVersion++; document.body.classList.remove('drawer-open'); opener?.focus(); });
  document.addEventListener('click', async e => {
    const open = e.target.closest('[data-open-cart]');
    if (open) {
      e.preventDefault();
      if (cartPending || drawerRead) return;
      if (pageCart) {
        pageCart.scrollIntoView({block: 'start'});
        pageCart.querySelector('input[type=number], .button, a')?.focus();
        return;
      }
      const version = ++drawerVersion;
      drawerRead = (async () => {
        try {
          const response = await fetch(open.href, {headers: {'X-Mahrukh-Drawer': '1'}});
          if (!response.ok) throw new Error();
          const html = await response.text();
          if (version !== drawerVersion) return;
          replaceCartContents(body, html); openDrawer();
        } catch { if (version === drawerVersion) window.location.href = open.href; }
      })();
      try { await drawerRead; } finally { drawerRead = null; }
    }
    if (e.target.closest('[data-close-cart]')) closeDrawer();
    if (e.target === drawer) { const r = drawer.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right) closeDrawer(); }
    const thumbnail = e.target.closest('[data-image]');
    if (thumbnail) {
      document.querySelector('#main-product-image').src = thumbnail.dataset.image;
      document.querySelectorAll('[data-image]').forEach(b => b.setAttribute('aria-pressed', String(b === thumbnail)));
    }
  });
  document.addEventListener('submit', async e => {
    const form = e.target;
    if (form.dataset.confirm && !window.confirm(form.dataset.confirm)) { e.preventDefault(); return; }
    if (!form.matches('[data-cart-form]')) return;
    e.preventDefault();
    if (cartPending) return;
    cartPending = true;
    const version = ++drawerVersion;
    const removing = e.submitter?.value === 'remove';
    const data = new FormData(form);
    if (e.submitter?.name) data.set(e.submitter.name, e.submitter.value);
    // A control named action shadows form.action in the DOM.
    const actionUrl = form.getAttribute('action');
    const buttons = [...document.querySelectorAll('[data-cart-form] button, [data-checkout-form] button')].map(button => [button, button.disabled]);
    buttons.forEach(([button]) => button.disabled = true);
    try {
      // Flask uses a signed session cookie. Wait for an earlier GET response
      // before mutating so its Set-Cookie cannot overwrite the newer cart.
      if (drawerRead) await drawerRead;
      const response = await fetch(actionUrl, {method: 'POST', body: data, headers: {'X-Mahrukh-Drawer': '1'}});
      if (!response.ok) {
        const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
        toast(doc.querySelector('main .page p:not(.eyebrow)')?.textContent || t('Unable to update the bag. Reload and try again.')); return;
      }
      const html = await response.text();
      replaceCartContents(pageCart || body, html);
      document.querySelectorAll('[data-cart-count]').forEach(el => { el.textContent = response.headers.get('X-Cart-Count'); el.closest('[data-open-cart]')?.setAttribute('aria-label', t('Shopping cart, {count} items', {count: el.textContent})); });
      // Update the visible page in place: no navigation prompt can strand an
      // old quote/token after the server has already changed the bag.
      if (!pageCart && version === drawerVersion) openDrawer();
      const visibleCart = drawer.open ? body : pageCart;
      visibleCart?.querySelector('input[type=number], .button, a')?.focus();
      toast(removing ? t('Item removed from your bag.') : t('Your bag is updated.'));
    } catch { toast(t('Connection interrupted. Reload the bag to check whether your update was saved.')); }
    finally { cartPending = false; buttons.forEach(([button, disabled]) => button.disabled = disabled); }
  });
})();
