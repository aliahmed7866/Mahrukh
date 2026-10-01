"""Optional Urdu facts never change inventory, identifiers or English source text."""
from contextlib import contextmanager
from html import unescape
import json
import re
import sqlite3
import unittest

from flask import template_rendered
import test_shop
from catalog import empty_details


class ProductI18nTests(unittest.TestCase):
    setUp = test_shop.ShopTests.setUp
    tearDown = test_shop.ShopTests.tearDown
    post = test_shop.ShopTests.post
    login = test_shop.ShopTests.login

    def translations(self, pid=1, **fields):
        with sqlite3.connect(self.database) as db:
            # Escaped Unicode must remain searchable in upgraded/older JSON.
            db.execute('INSERT INTO product_translations VALUES(?,?) ON CONFLICT(product_id) DO UPDATE SET data=excluded.data',
                       (pid, json.dumps(fields)))

    @contextmanager
    def rendered(self):
        contexts = []
        def record(sender, template, context, **extra):
            contexts.append(context)
        template_rendered.connect(record, self.app)
        try:
            yield contexts
        finally:
            template_rendered.disconnect(record, self.app)

    def edit_fields(self, **changes):
        html = self.client.get('/admin/product/1').get_data(as_text=True)
        version = unescape(re.search('name="edit_version" value="([^"]+)"', html).group(1))
        return dict(name='Mehr · Emerald', category='Stitched / Pret', price=6490,
                    fabric='Cotton', description='Photo fixture', sizes=['M'],
                    images='https://example.com/product.jpg', stock_M=20,
                    active='on', edit_version=version, **changes)

    def test_translations_available_in_catalog_detail_saved_and_related(self):
        self.translations(name='مہر', fabric='سوتی کپڑا', care='ہاتھ سے دھوئیں')
        with self.rendered() as contexts:
            self.client.get('/')
        p = next(item for item in contexts[-1]['products'] if item['id'] == 1)
        self.assertEqual(p['translations']['name'], 'مہر')
        self.assertIs(p['translations'], p['details']['translations'])
        with self.rendered() as contexts:
            self.client.get('/product/1')
        self.assertEqual(contexts[-1]['item']['translations']['care'], 'ہاتھ سے دھوئیں')
        self.post('/saved/1', {'action': 'save'})
        with self.rendered() as contexts:
            self.client.get('/saved')
        self.assertEqual(contexts[-1]['products'][0]['translations']['name'], 'مہر')
        with self.rendered() as contexts:
            self.client.get('/product/6')
        related = next(p for p in contexts[-1]['related'] if p['id'] == 1)
        self.assertEqual(related['translations']['name'], 'مہر')

    def test_search_finds_either_language_and_garment_facts(self):
        self.translations(name='مہر', description='پھولوں کی کڑھائی', care='ہاتھ سے دھوئیں')
        with sqlite3.connect(self.database) as db:
            db.execute('INSERT INTO product_details VALUES(?,?)',
                       (1, json.dumps(dict(empty_details(), craft='Botanical embroidery'))))
        for locale in ('en', 'ur'):
            for query in ('Emerald', 'مہر', 'کڑھائی', 'دھوئیں', 'Botanical'):
                with self.subTest(locale=locale, query=query), self.rendered() as contexts:
                    response = self.client.get('/', query_string={'q': query, 'lang': locale})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual([p['id'] for p in contexts[-1]['products']], [1])

    def test_editor_saves_optional_urdu_and_preserves_omitted_translations(self):
        self.login()
        self.assertEqual(self.post('/admin/product/1', self.edit_fields(
            ur_name='مہر', ur_fabric='سوتی کپڑا', ur_description='اصل پراڈکٹ',
            detail_care='Hand wash', ur_care='ہاتھ سے دھوئیں')).status_code, 303)
        with sqlite3.connect(self.database) as db:
            before = db.execute('SELECT name,price FROM products WHERE id=1').fetchone()
            data = json.loads(db.execute('SELECT data FROM product_translations WHERE product_id=1').fetchone()[0])
            self.assertEqual(data['care'], 'ہاتھ سے دھوئیں')
            self.assertEqual(before, ('Mehr · Emerald', 6490))
            self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0], 20)
        self.assertEqual(self.post('/admin/product/1', self.edit_fields()).status_code, 303)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(json.loads(db.execute('SELECT data FROM product_translations WHERE product_id=1').fetchone()[0]), data)
        self.assertEqual(self.post('/admin/product/1', self.edit_fields(ur_care='')).status_code, 303)
        with sqlite3.connect(self.database) as db:
            self.assertNotIn('care', json.loads(db.execute('SELECT data FROM product_translations WHERE product_id=1').fetchone()[0]))
        self.assertEqual(self.post('/admin/product/1/delete').status_code, 303)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM product_translations').fetchone()[0], 0)

    def test_translation_edits_obey_versioning_limits_and_html_escaping(self):
        self.login()
        stale = self.edit_fields()
        self.translations(name='تازہ نام')
        self.assertEqual(self.post('/admin/product/1', stale).status_code, 409)
        invalid = self.post('/admin/product/1', self.edit_fields(ur_name='الف' * 40))
        self.assertIn('Urdu product name must be at most 100', invalid.get_data(as_text=True))
        with sqlite3.connect(self.database) as db:
            self.assertEqual(json.loads(db.execute('SELECT data FROM product_translations WHERE product_id=1').fetchone()[0])['name'], 'تازہ نام')
        self.translations(name='<script>alert(1)</script>')
        html = self.client.get('/product/1?lang=ur').get_data(as_text=True)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>alert(1)</script>', html)

    def test_size_query_is_allowlisted_without_changing_bag(self):
        self.post('/cart', dict(id=1, size='M', quantity=2))
        for size, expected in [('M', 'M'), ('not-a-size', '')]:
            with self.rendered() as contexts:
                self.client.get('/product/1', query_string={'lang': 'ur', 'size': size})
            self.assertEqual(contexts[-1]['selected_size'], expected)
        with self.client.session_transaction() as session:
            self.assertEqual(session['cart']['1:M']['quantity'], 2)


if __name__ == '__main__':
    unittest.main()
