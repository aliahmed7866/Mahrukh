// Validate actual non-selling preview script against public fixtures, without a browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../preview/preview.js'), 'utf8');
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, '../preview/products.json'), 'utf8'));
function element() {
  return { children: [], events: {}, textContent: '', append(...children) { this.children.push(...children); }, replaceChildren() { this.children = []; }, setAttribute() {}, addEventListener(name, callback) { this.events[name] = callback; }, focus() {} };
}
function run(stored, blocked = false) {
  const events = {}, lines = element(), notice = element(), counter = element();
  counter.closest = () => null;
  const dialog = () => ({ addEventListener() {}, showModal() {}, querySelector: () => element() });
  const nodes = { '#demo-cart': dialog(), '#demo-help': dialog(), '#demo-catalog': { textContent: JSON.stringify(catalog) }, '#demo-cart-lines': lines, '#demo-cart .notice': notice, '#size-preview': element(), '[name=demo-size]:checked': { value: 'M' } };
  let saved;
  vm.runInNewContext(source, {
    window: { MahrukhI18n: { t: (text, values = {}) => text.replace(/\{(\w+)\}/g, (_, key) => values[key] ?? key) } },
    document: { querySelector: selector => nodes[selector] || null, querySelectorAll: selector => selector === '[data-cart-count]' ? [counter] : [], createElement: element, addEventListener: (name, callback) => { events[name] = callback; }, body: { classList: { add() {}, remove() {} } } },
    sessionStorage: { getItem: () => stored, setItem: (key, value) => { if (blocked) throw new Error('blocked'); saved = JSON.parse(value); } },
    URL, URLSearchParams, location: { search: '' }
  });
  const text = node => [node.textContent, ...node.children.map(text)].join(' ');
  return { counter, lines, notice, text: () => text(lines), add() { const product = catalog[0]; events.click({ target: { closest: selector => selector === '[data-demo-add]' ? { dataset: { id: String(product.id), name: product.name, price: String(product.price) } } : null } }); return saved; } };
}
const product = catalog[0];
const result = run(JSON.stringify([
  { id: product.id, size: 'M', quantity: 2, name: 'Untrusted name', price: 1 },
  { id: product.id, size: 'M', quantity: 1 }, // duplicate
  { id: 999999, size: 'M', quantity: 2 },
  { id: product.id, size: 'fake', quantity: 2 },
  { id: product.id, size: 'L', quantity: 11 }, null
]));
assert.equal(result.counter.textContent, 2);
assert.match(result.text(), new RegExp(product.name));
assert.doesNotMatch(result.text(), /Untrusted name/);
assert.ok(result.text().includes((product.price * 2).toLocaleString('en-PK')));
const saved = result.add();
assert.equal(saved.length, 1);
assert.equal(saved[0].quantity, 3);
assert.equal(saved[0].price, product.price);
assert.equal(saved[0].name, product.name);
assert.equal(run('{broken').counter.textContent, 0);
assert.equal(run('{}').counter.textContent, 0);
const blocked = run('[]', true);
blocked.add();
assert.equal(blocked.counter.textContent, 1);
assert.match(blocked.notice.textContent, /Browser storage is unavailable/);
console.log('Preview sample bag: 12 assertions passed.');
