// Exercise live cart request paths without requiring a browser dependency.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const script = fs.readFileSync(path.join(__dirname, '../static/shop.js'), 'utf8');
async function scenario(pathname, drawerOpen, responseOk = true) {
  const events = {};
  const fetched = [];
  const focused = [];
  const toast = {};
  const button = {};
  let count = 0;
  const body = { innerHTML: '', querySelector: () => ({ focus: () => focused.push('line') }) };
  const drawer = { open: drawerOpen, addEventListener() {}, showModal() { this.open = true; } };
  const location = { pathname, href: '' };
  const document = {
    activeElement: { focus() {} }, body: { classList: { add() {}, remove() {} } },
    querySelector: selector => ({ '#cart-drawer': drawer, '#cart-body': body, '#toast': toast }[selector]),
    querySelectorAll: () => [{ set textContent(value) { count = value; }, get textContent() { return count; }, closest: () => null }],
    addEventListener: (name, callback) => { events[name] = callback; }
  };
  const form = {
    // Named controls shadow the built-in DOM property.
    action: { toString: () => '[object RadioNodeList]' },
    dataset: {}, matches: () => true,
    getAttribute: name => name === 'action' ? '/cart?lang=ur' : null,
    querySelectorAll: () => [button]
  };
  class FormData { set() {} }
  vm.runInNewContext(script, {
    document, window: {}, location, FormData,
    fetch: async (url, options) => {
      fetched.push({ url, options });
      if (!responseOk) throw new Error('offline');
      return { ok: true, text: async () => 'updated bag', headers: { get: () => '2' } };
    },
    clearTimeout() {}, setTimeout() {}
  });
  let prevented = false;
  await events.submit({ target: form, submitter: { name: 'action', value: 'update' }, preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(fetched[0].url, '/cart?lang=ur', 'named action buttons do not corrupt the request URL');
  assert.equal(fetched[0].options.method, 'POST');
  assert.equal(button.disabled, false, 'controls are re-enabled');
  if (responseOk) {
    assert.equal(body.innerHTML, 'updated bag');
    assert.equal(count, '2');
    if (['/cart', '/checkout'].includes(pathname) && !drawerOpen) {
      assert.equal(location.href, '/cart?lang=ur', 'GET navigation avoids replaying failed checkout POST');
    } else {
      assert.equal(location.href, '');
      assert.equal(drawer.open, true);
    }
    if (drawerOpen) assert.deepEqual(focused, ['line']);
  } else {
    assert.equal(location.href, '');
    assert.match(toast.textContent, /Connection interrupted/);
  }
}
(async () => {
  await scenario('/cart', false);
  await scenario('/checkout', false);
  await scenario('/product/1', false);
  await scenario('/product/1', true);
  await scenario('/checkout', false, false);
  console.log('Cart request behavior: 5 scenarios passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
