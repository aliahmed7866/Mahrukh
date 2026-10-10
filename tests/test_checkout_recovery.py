"""Checkout corrections preserve input only in the current HTML response."""
import sqlite3
import unittest
from html.parser import HTMLParser

import test_shop


class FormParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

    def named(self, name):
        return [attrs for tag, attrs in self.nodes if attrs.get('name') == name]


class CheckoutRecoveryTests(unittest.TestCase):
    setUp = test_shop.ShopTests.setUp
    tearDown = test_shop.ShopTests.tearDown
    post = test_shop.ShopTests.post
    quote = test_shop.ShopTests.quote
    order_fields = test_shop.ShopTests.order_fields

    def fields(self):
        self.post('/cart', dict(id=1, size='M', quantity=1))
        return self.order_fields()

    def test_invalid_phone_retains_details_and_corrected_retry_creates_one_order(self):
        fields = self.fields()
        response = self.post('/checkout', {**fields, 'contact': 'not a number'})
        self.assertEqual(response.status_code, 400)
        html = response.get_data(as_text=True)
        form = FormParser(html)
        self.assertEqual(form.named('name')[0]['value'], fields['name'])
        self.assertEqual(form.named('contact')[0]['value'], 'not a number')
        self.assertEqual(form.named('contact')[0]['aria-invalid'], 'true')
        self.assertEqual(form.named('contact')[0]['aria-describedby'], 'checkout-error-contact')
        self.assertIn('href="#checkout-contact"', html)
        self.assertIn('data-checkout-errors', html)
        self.assertIn('data-checkout-recovered="true"', html)
        self.assertIn('href="/cart?lang=ur"', html)
        self.assertNotIn('href="/checkout?lang=ur"', html)
        self.assertIn('Street #2</textarea>', html)
        self.assertIn('value="Lahore" selected', html)
        self.assertIn('checked', form.named('payment_method')[0])
        self.assertIn('checked', form.named('agree')[0])
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM orders').fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0], 20)
        # Retry directly using the returned form, without a bag reload.
        for key in ('checkout_token', 'quote_hash'):
            fields[key] = form.named(key)[0]['value']
        accepted = self.post('/checkout', fields)
        self.assertEqual(accepted.status_code, 303)
        self.assertEqual(self.post('/checkout', fields).location, accepted.location)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM orders').fetchone()[0], 1)

    def test_all_errors_are_shown_together_without_preselecting_invalid_choices(self):
        fields = self.fields()
        response = self.post('/checkout', {**fields, 'name': '', 'contact': '-------', 'city': 'Elsewhere', 'payment_method': 'hosted', 'agree': ''})
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 400)
        for field in ('name', 'contact', 'city', 'payment_method', 'agree'):
            self.assertIn('href="#checkout-' + field + '"', html)
        form = FormParser(html)
        self.assertNotIn('checked', form.named('agree')[0])
        self.assertFalse(any('checked' in attrs for attrs in form.named('payment_method')))

    def test_retained_values_are_escaped_and_not_persisted(self):
        fields = self.fields()
        payload = '\"><script>alert(1)</script>'
        response = self.post('/checkout', {**fields, 'name': payload, 'address': '</textarea><script>alert(2)</script>', 'contact': 'bad'})
        html = response.get_data(as_text=True)
        self.assertNotIn('<script>alert(', html)
        self.assertEqual(FormParser(html).named('name')[0]['value'], payload)
        with self.client.session_transaction() as session:
            self.assertFalse(any(key in session for key in ('name', 'contact', 'city', 'address', 'checkout_values')))
        fresh = self.client.get('/cart').get_data(as_text=True)
        self.assertNotIn('alert(1)', fresh)
        self.assertNotIn('alert(2)', fresh)

    def test_invalid_form_does_not_refresh_a_stale_quote(self):
        fields = self.fields()
        with sqlite3.connect(self.database) as db:
            db.execute('UPDATE products SET price=7000 WHERE id=1')
        response = self.post('/checkout', {**fields, 'contact': 'bad'})
        quote = FormParser(response.get_data(as_text=True)).named('quote_hash')[0]['value']
        self.assertEqual(quote, fields['quote_hash'])
        self.assertEqual(self.post('/checkout', {**fields, 'quote_hash': quote}).status_code, 409)

    def test_cart_refresh_uses_fresh_server_tokens_and_total(self):
        fields = self.fields()
        page = self.client.get('/cart').get_data(as_text=True)
        self.assertIn('id="cart-page-contents"', page)
        response = self.post('/cart', dict(action='update', id=1, size='M', quantity=2),
                             headers={'X-Mahrukh-Drawer': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Cart-Count'], '2')
        fresh = FormParser(response.get_data(as_text=True))
        self.assertNotEqual(fresh.named('checkout_token')[0]['value'], fields['checkout_token'])
        self.assertNotIn('checked', fresh.named('agree')[0])
        self.assertEqual(self.post('/checkout', fields).status_code, 400)
        for key in ('checkout_token', 'quote_hash'):
            fields[key] = fresh.named(key)[0]['value']
        self.assertEqual(self.post('/checkout', fields).status_code, 303)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT total FROM orders').fetchone()[0], 13230)

    def test_urdu_recovery_and_csrf_still_required(self):
        fields = self.fields()
        response = self.post('/checkout?lang=ur', {**fields, 'contact': 'bad'})
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn('lang="ur" dir="rtl"', html)
        self.assertIn('براہ کرم اپنے آرڈر کی تفصیلات دوبارہ دیکھ لیں۔', html)
        self.assertNotIn('Enter a valid contact phone number.', html)
        self.assertIn('action="/checkout?lang=ur"', html)
        self.assertEqual(self.client.post('/checkout', data=fields).status_code, 400)


if __name__ == '__main__':
    unittest.main()
