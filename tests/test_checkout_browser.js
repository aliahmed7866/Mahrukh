// Dependency-free tests of the live checkout draft guard (no DOM/browser QA).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
let forms = [];
const documentEvents = {};
const windowEvents = {};
const document = {
  body: { dataset: {} }, documentElement: { lang: 'en' },
  querySelector: () => null,
  querySelectorAll: selector => selector.includes('data-checkout-form') ? forms : [],
  addEventListener: (name, callback) => { documentEvents[name] = callback; }
};
const window = { addEventListener: (name, callback) => { windowEvents[name] = callback; } };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../static/i18n.js'), 'utf8'), {
  document, window, URL, URLSearchParams, location: { search: '', hash: '', href: 'https://shop.example/cart' }
});
const dirty = window.MahrukhI18n.hasUnsavedCheckout;
assert.equal(dirty(), false);
const field = { name: 'name', type: 'text', value: 'A & B', defaultValue: 'A & B' };
const form = { dataset: {}, elements: [field], matches: () => true };
forms = [form];
assert.equal(dirty(), false, 'unchanged ordinary form uses original dirty semantics');
form.dataset.checkoutRecovered = 'true';
assert.equal(dirty(), true, 'server-returned defaults are still unsent');
let prevented = false;
windowEvents.beforeunload({ preventDefault: () => { prevented = true; } });
assert.equal(prevented, true, 'recovered values trigger the navigation guard');
documentEvents.submit({ target: form });
assert.equal(dirty(), false, 'placing the order does not prompt about leaving');
windowEvents.pageshow();
assert.equal(dirty(), true, 'back navigation restores the guard');
field.value = '';
assert.equal(dirty(), false, 'cleared recovery form is no longer dirty');
form.elements = [{ name: 'agree', type: 'checkbox', checked: false, defaultChecked: true }];
assert.equal(dirty(), false);
form.elements[0].checked = true;
assert.equal(dirty(), true);
form.elements[0].disabled = true;
assert.equal(dirty(), false);
console.log('Checkout draft guard: 10 assertions passed.');
