"""Bilingual checkout preserves the original monetary and privacy contracts."""
import json
import re
import sqlite3
import unittest
from html import unescape
from urllib.parse import parse_qs, urlsplit

import test_shop
from commerce import TRANSLATABLE_SETTINGS, validate_settings
from i18n import t, use_locale


class CommerceLanguageTests(unittest.TestCase):
    setUp = test_shop.ShopTests.setUp
    tearDown = test_shop.ShopTests.tearDown
    post = test_shop.ShopTests.post
    login = test_shop.ShopTests.login
    quote = test_shop.ShopTests.quote
    order_fields = test_shop.ShopTests.order_fields

    def setting(self, **changes):
        with sqlite3.connect(self.database) as db:
            data = json.loads(db.execute('SELECT data FROM shop_settings').fetchone()[0])
            data.update(changes)
            db.execute('UPDATE shop_settings SET data=?', (json.dumps(data),))
        return data

    def translate_product(self, **values):
        with sqlite3.connect(self.database) as db:
            db.execute('INSERT INTO product_translations(product_id,data) VALUES(1,?) '
                       'ON CONFLICT(product_id) DO UPDATE SET data=excluded.data',
                       (json.dumps(values),))

    def place(self):
        self.post('/cart', dict(id=1, size='M', quantity=1))
        response = self.post('/checkout', self.order_fields())
        self.assertEqual(response.status_code, 303, response.get_data(as_text=True))
        return urlsplit(response.location).path

    def test_optional_seller_fields_save_and_validate_without_requiring_urdu(self):
        fields = self.setting(personal_note='Welcome', shipping_ur='ا' * 2500)
        form = {key: ('on' if value is True else str(value))
                for key, value in fields.items() if value is not False}
        saved = validate_settings(form)
        self.assertEqual(saved['shipping_ur'], 'ا' * 2500)
        self.assertEqual(saved['terms_ur'], '')
        with self.assertRaises(ValueError):
            validate_settings({**form, 'personal_note_ur': 'ا' * 801})
        with self.assertRaises(ValueError):
            validate_settings({**form, 'privacy_ur': 'ا' * 10001})
        # A settings tab opened before the bilingual upgrade keeps unseen values.
        legacy = {key: value for key, value in form.items() if not key.endswith('_ur')}
        self.assertEqual(validate_settings(legacy, saved)['shipping_ur'], 'ا' * 2500)
        self.login()
        html = self.client.get('/admin/settings?lang=ur').get_data(as_text=True)
        for key in TRANSLATABLE_SETTINGS:
            self.assertIn('name="' + key + '_ur"', html)
        self.assertIn('lang="ur" dir="rtl"', html)
        self.assertIn('Save shop settings', html)
        form['personal_note_ur'] = 'خوش آمدید'
        self.assertEqual(self.post('/admin/settings', form).status_code, 303)
        self.assertIn('خوش آمدید', self.client.get('/?lang=ur').get_data(as_text=True))

    def test_language_switch_preserves_quote_token_and_existing_cart(self):
        self.post('/cart', dict(id=1, size='M', quantity=2))
        first = self.quote()
        with self.client.session_transaction() as state:
            before = {key: state.get(key) for key in ('cart', 'order_owner', 'checkout_token', 'csrf')}
        response = self.client.get('/cart?lang=ur')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.quote(), first)
        with self.client.session_transaction() as state:
            self.assertEqual({key: state.get(key) for key in before}, before)
        response = self.post('/checkout', {**self.order_fields(), **first})
        self.assertEqual(response.status_code, 303)
        with sqlite3.connect(self.database) as db:
            total, merchant = db.execute('SELECT total,merchant FROM orders').fetchone()
        self.assertEqual(total, 13230)
        self.assertEqual(json.loads(merchant)['locale'], 'ur')

    def test_full_length_urdu_policies_fit_the_seller_settings_request_limit(self):
        self.login()
        settings = self.setting(**{key + '_ur': 'آ' * 10000
                                  for key in ('shipping', 'returns', 'privacy', 'terms')})
        form = {key: ('on' if value is True else str(value))
                for key, value in settings.items() if value is not False}
        response = self.post('/admin/settings', form)
        self.assertEqual(response.status_code, 303)
        with sqlite3.connect(self.database) as db:
            saved = json.loads(db.execute('SELECT data FROM shop_settings').fetchone()[0])
        self.assertEqual(saved['terms_ur'], 'آ' * 10000)

    def test_translation_edits_invalidate_reviewed_quote_even_in_english(self):
        self.post('/cart', dict(id=1, size='M', quantity=1))
        fields = self.order_fields()
        self.translate_product(name='مہر', description='اصل تفصیل')
        self.assertEqual(self.post('/checkout', fields).status_code, 409)
        fields = self.order_fields()
        self.setting(terms_ur='شرائط کا اصل متن')
        self.assertEqual(self.post('/checkout', fields).status_code, 409)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM orders').fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0], 20)

    def test_order_snapshots_both_languages_and_draft_uses_selected_language(self):
        self.translate_product(name='مہر', description='اصل تفصیل', care='ہاتھ سے دھوئیں')
        self.setting(terms_ur='اصل شرائط', dispatch_note_ur='تین سے پانچ دن')
        self.client.get('/?lang=ur')
        receipt = self.place()
        with sqlite3.connect(self.database) as db:
            items, policies, merchant = map(json.loads, db.execute('SELECT items,policies,merchant FROM orders').fetchone())
        self.assertEqual(items[0]['name'], 'Mehr · Emerald')
        self.assertEqual(items[0]['translations']['name'], 'مہر')
        self.assertEqual(items[0]['details']['translations']['care'], 'ہاتھ سے دھوئیں')
        self.assertEqual(policies['terms'], 'Test terms')
        self.assertEqual(policies['terms_ur'], 'اصل شرائط')
        self.assertEqual(merchant['locale'], 'ur')
        self.assertEqual(merchant['dispatch_note'], '3–5 days')
        self.translate_product(name='بدلا ہوا نام')
        self.setting(terms_ur='بدلی ہوئی شرائط', dispatch_note_ur='بدلا ہوا وقت')
        html = self.client.get(receipt).get_data(as_text=True)
        self.assertIn('اصل شرائط', html)
        self.assertNotIn('بدلی ہوئی شرائط', html)
        drafts = [parse_qs(urlsplit(unescape(link)).query)['text'][0]
                  for link in re.findall(r'href="(https://wa.me/[^\"]+)"', html)]
        draft = next(value for value in drafts if receipt.rsplit('/', 1)[-1] in value)
        self.assertIn('مہر | M | تعداد 1 | PKR 6,490', draft)
        self.assertIn('PKR 6,740', draft)
        self.assertNotIn('بدلا ہوا نام', draft)
        english = self.client.get(receipt + '?lang=en').get_data(as_text=True)
        self.assertIn('Mehr%20%C2%B7%20Emerald', english)
        self.assertIn('Test terms', english)
        self.assertEqual(self.app.test_client().get(receipt).status_code, 404)

    def test_legacy_english_receipts_render_without_snapshot_backfill(self):
        receipt = self.place()
        with sqlite3.connect(self.database) as db:
            items, policies, merchant = map(json.loads, db.execute('SELECT items,policies,merchant FROM orders').fetchone())
            merchant.pop('locale')
            merchant = {key: value for key, value in merchant.items() if not key.endswith('_ur')}
            policies = {key: value for key, value in policies.items() if not key.endswith('_ur')}
            for item in items:
                item.pop('translations')
                item['details'].pop('translations', None)
            db.execute('UPDATE orders SET items=?,policies=?,merchant=?', tuple(map(json.dumps, (items, policies, merchant))))
        response = self.client.get(receipt + '?lang=ur')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test terms', response.get_data(as_text=True))
        self.assertIn('lang="en" dir="ltr"', response.get_data(as_text=True))
        with sqlite3.connect(self.database) as db:
            saved = json.loads(db.execute('SELECT merchant FROM orders').fetchone()[0])
            self.assertNotIn('locale', saved)

    def test_checkout_validation_is_translated_without_weakening_checks(self):
        self.post('/cart', dict(id=1, size='M', quantity=1))
        fields = self.order_fields()
        self.client.get('/cart?lang=ur')
        cases = [({'agree': ''}, 'Please read and accept the terms and privacy notice.'),
                 ({'contact': 'invalid'}, 'Enter a valid contact phone number.'),
                 ({'city': 'unsupported'}, 'Please choose one of our listed delivery cities.'),
                 ({'payment_method': 'invalid'}, 'Choose an available payment method.')]
        for change, message in cases:
            response = self.post('/checkout', {**fields, **change})
            self.assertEqual(response.status_code, 400)
            with use_locale('ur'):
                translated = t(message)
            self.assertNotEqual(translated, message)
            self.assertIn(translated, response.get_data(as_text=True))
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM orders').fetchone()[0], 0)

    def test_translated_receipts_and_english_fallbacks_escape_seller_markup(self):
        markup = '<script>alert("seller text")</script>'
        self.translate_product(name=markup)
        self.setting(terms=markup, terms_ur=markup, business_address=markup)
        receipt = self.place()
        for locale in ('en', 'ur'):
            response = self.client.get(receipt + '?lang=' + locale)
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertNotIn(markup, html)
            self.assertIn('&lt;script&gt;', html)
        self.assertIn('class="english-fallback"', html)
        self.assertIn('lang="en" dir="ltr"', html)


if __name__ == '__main__':
    unittest.main()
