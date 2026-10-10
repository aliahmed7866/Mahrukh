// Exercise actual live cart code with a small DOM stub; not visual browser QA.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const script = fs.readFileSync(path.join(__dirname, '../static/shop.js'), 'utf8');
function checkout(overrides = {}) {
  const fields = Object.fromEntries(['name', 'contact', 'city', 'address'].map(name => [name, { value: overrides[name] || '' }]));
  const payments = [{ value: 'cod', checked: overrides.payment === 'cod' }, { value: 'transfer', checked: overrides.payment === 'transfer' }];
  return {
    dataset: {}, fields, payments, consent: Boolean(overrides.consent),
    token: overrides.token || 'fresh-token', notice: null,
    querySelector(selector) {
      if (selector === '[name="payment_method"]:checked') return payments.find(field => field.checked);
      return fields[selector.match(/name="(\w+)"/)?.[1]];
    },
    querySelectorAll: () => payments,
    prepend(notice) { this.notice = notice; }
  };
}
async function scenario({ page = false, recovered = false, drawerOpen = false, offline = false, empty = false, repeat = false, closeDuringUpdate = false, readBeforeUpdate = false } = {}) {
  const events = {}, fetched = [], focused = [], toast = {};
  const button = { disabled: false }, previouslyDisabled = { disabled: true };
  const initial = checkout({ name: 'A & B', contact: '03001234567', city: 'Lahore', address: 'Street #2', payment: 'cod', consent: true, token: 'old-token' });
  const region = {
    form: initial, html: '', scrolled: false,
    querySelector: selector => selector === '[data-checkout-form]' ? region.form : { focus: () => focused.push('line') },
    set innerHTML(value) { this.html = value; this.form = empty ? null : checkout(); },
    scrollIntoView() { this.scrolled = true; }
  };
  const unusedDrawerBody = { querySelector: () => null };
  const drawerEvents = {};
  const drawer = { open: drawerOpen, addEventListener(name, callback) { drawerEvents[name] = callback; }, showModal() { this.open = true; } };
  const location = { pathname: recovered ? '/checkout' : page ? '/cart' : '/product/1', href: '' };
  let count = 0, resolveFetch;
  const pending = [];
  const countLabel = { set textContent(value) { count = value; }, get textContent() { return count; }, closest: () => null };
  const document = {
    activeElement: { focus() {} }, body: { classList: { add() {}, remove() {} } },
    querySelector: selector => ({ '#cart-drawer': drawer, '#cart-body': page ? unusedDrawerBody : region, '#cart-page-contents': page ? region : null, '#toast': toast }[selector]),
    querySelectorAll: selector => selector === '[data-cart-count]' ? [countLabel] : [button, previouslyDisabled],
    createElement: () => ({}),
    addEventListener: (name, callback) => { events[name] = callback; }
  };
  const form = {
    action: { toString: () => '[object RadioNodeList]' }, dataset: {}, matches: () => true,
    getAttribute: name => name === 'action' ? '/cart?lang=ur' : null
  };
  class FormData { set() {} }
  vm.runInNewContext(script, {
    document, window: {}, location, FormData,
    fetch: (url, options) => {
      fetched.push({ url, options });
      if (offline) return Promise.reject(new Error('offline'));
      return new Promise(resolve => { resolveFetch = () => resolve({ ok: true, text: async () => options.method === 'POST' ? 'updated bag' : 'stale bag', headers: { get: () => '2' } }); pending.push(resolveFetch); });
    }, clearTimeout() {}, setTimeout() {}
  });
  let prevented = 0;
  const event = { target: form, submitter: { name: 'action', value: 'update' }, preventDefault() { prevented++; } };
  const opening = readBeforeUpdate ? events.click({ target: { closest: selector => selector === '[data-open-cart]' ? { href: '/cart?lang=ur' } : null }, preventDefault() {} }) : null;
  const operation = events.submit(event);
  if (!offline) {
    assert.equal(button.disabled, true);
    if (readBeforeUpdate) {
      assert.equal(fetched.length, 1, 'mutation waits for earlier GET, including Set-Cookie');
      pending[0]();
      await opening;
      assert.equal(fetched.length, 2);
    }
    if (repeat) {
      await events.submit(event);
      await events.click({ target: { closest: selector => selector === '[data-open-cart]' ? { href: '/cart?lang=ur' } : null }, preventDefault() {} });
    }
    if (closeDuringUpdate) { drawer.open = false; drawerEvents.close(); }
    // Edits typed while the network is busy must win over an early snapshot.
    initial.fields.address.value = 'New address typed while waiting';
    resolveFetch();
  }
  await operation;
  assert.ok(prevented >= 1);
  if (opening) await opening;
  assert.equal(fetched.length, readBeforeUpdate ? 2 : 1, 'parallel cart mutations are not submitted');
  const mutation = fetched.at(-1);
  assert.equal(mutation.url, '/cart?lang=ur', 'named action controls cannot shadow the URL');
  assert.equal(mutation.options.method, 'POST');
  assert.equal(button.disabled, false);
  assert.equal(previouslyDisabled.disabled, true);
  assert.equal(location.href, '', 'cart refresh never navigates or replays checkout POST');
  if (offline) {
    assert.equal(region.form, initial);
    assert.match(toast.textContent, /Connection interrupted/);
  } else {
    assert.equal(region.html, 'updated bag');
    assert.equal(count, '2');
    assert.equal(drawer.open, closeDuringUpdate ? false : page ? drawerOpen : true);
    assert.deepEqual(focused, closeDuringUpdate ? [] : ['line']);
    if (!empty) {
      assert.equal(region.form.fields.name.value, 'A & B');
      assert.equal(region.form.fields.address.value, 'New address typed while waiting');
      assert.equal(region.form.token, 'fresh-token');
      assert.equal(region.form.consent, false);
      assert.equal(region.form.payments[0].checked, true);
      assert.equal(region.form.dataset.checkoutRecovered, 'true');
      assert.match(region.form.notice.textContent, /Review the updated total/);
    } else assert.equal(region.form, null);
  }
  if (page) {
    const before = fetched.length;
    await events.click({ target: { closest: selector => selector === '[data-open-cart]' ? { href: '/cart?lang=ur' } : null }, preventDefault() {} });
    assert.equal(fetched.length, before, 'the bag link on the bag page does not replace the draft');
    assert.equal(region.scrolled, true);
  }
}
(async () => {
  await scenario({ page: true });
  await scenario({ page: true, recovered: true });
  await scenario();
  await scenario({ drawerOpen: true });
  await scenario({ page: true, offline: true });
  await scenario({ page: true, empty: true });
  await scenario({ repeat: true });
  await scenario({ drawerOpen: true, closeDuringUpdate: true });
  await scenario({ readBeforeUpdate: true });
  console.log('Cart request behavior: 9 scenarios passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
