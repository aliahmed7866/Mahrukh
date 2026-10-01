"""Locale continuity, safe fallbacks and language URLs independent of JS."""
import sqlite3
import unittest
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

import test_shop
from i18n import COOKIE, content, current_locale, localized, t, use_locale


class LanguageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = {}

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'a' and 'data-language-link' in values:
            self.links[values['hreflang']] = values


class LanguageTests(unittest.TestCase):
    setUp = test_shop.ShopTests.setUp
    tearDown = test_shop.ShopTests.tearDown
    post = test_shop.ShopTests.post
    login = test_shop.ShopTests.login

    def test_explicit_choice_cookie_default_and_attributes(self):
        self.assertIn('<html lang="en" dir="ltr">', self.client.get('/').text)
        response = self.client.get('/?lang=ur')
        self.assertIn('<html lang="ur" dir="rtl">', response.text)
        self.assertEqual(response.headers['Content-Language'], 'ur')
        cookie = self.client.get_cookie(COOKIE)
        self.assertEqual(cookie.value, 'ur')
        self.assertTrue(cookie.http_only)
        self.assertEqual(cookie.same_site, 'Lax')
        self.assertIn('<html lang="ur" dir="rtl">', self.client.get('/saved').text)
        self.assertIn('<html lang="en" dir="ltr">', self.client.get('/saved?lang=en').text)
        self.assertIn('<html lang="en" dir="ltr">', self.client.get('/?lang=unexpected').text)

    def test_selector_retains_filters_and_navigation_without_cookies(self):
        client = self.app.test_client(use_cookies=False)
        response = client.get('/?lang=ur&q=Cotton&category=Abayas&size=M&budget=8000&sort=price-low')
        parser = LanguageLinks()
        parser.feed(response.text)
        args = parse_qs(urlsplit(parser.links['en']['href']).query)
        self.assertEqual(args, dict(lang=['en'], q=['Cotton'],category=['Abayas'],size=['M'],budget=['8000'],sort=['price-low']))
        self.assertEqual(parser.links['ur']['aria-current'], 'true')
        self.assertIn('/saved?lang=ur', response.text)
        self.assertIn('name="lang" value="ur"', response.text)

    def test_switch_does_not_mutate_cart_favourites_or_inventory(self):
        self.post('/cart', dict(id=1, size='M', quantity=2))
        self.post('/saved/2', dict(action='save'))
        with self.client.session_transaction() as state:
            before = dict(state)
        for route in ('/?lang=ur', '/product/1?size=M&lang=en', '/saved?lang=ur', '/cart?lang=en'):
            self.assertEqual(self.client.get(route).status_code, 200)
        with self.client.session_transaction() as state:
            for key in ('cart', 'saved', 'checkout_token', 'csrf'):
                self.assertEqual(state[key], before[key])
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(connection.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0],20)
            self.assertEqual(connection.execute('SELECT count(*) FROM orders').fetchone()[0], 0)

    def test_fallback_escape_isolation_and_no_invented_product_translation(self):
        product = {'name': 'English <script>alert(1)</script>'}
        with use_locale('ur'):
            self.assertEqual(current_locale(), 'ur')
            self.assertEqual(localized(product, 'name'), product['name'])
            fallback = str(content(product, 'name'))
            self.assertIn('lang="en" dir="ltr"', fallback)
            self.assertIn('fallback-label', fallback)
            self.assertIn('&lt;script&gt;', fallback)
            self.assertNotIn('<script>', fallback)
            translated = str(content(dict(product, translations={'name': 'اردو <img onerror=alert(1)>'}), 'name'))
            self.assertIn('lang="ur" dir="rtl"', translated)
            self.assertIn('&lt;img', translated)
            self.assertNotIn('fallback-label', translated)
        self.assertEqual(current_locale(), 'en')

    def test_urdu_errors_are_localized_and_admin_stays_english(self):
        self.client.get('/?lang=ur')
        response = self.client.post('/cart', data=dict(id=1, size='M'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('<html lang="ur" dir="rtl">', response.text)
        self.assertNotIn('This form expired. Reload the page and try again.</p>', response.text)
        self.login()
        self.assertIn('<html lang="en" dir="ltr">', self.client.get('/admin').text)
        self.assertIn('<html lang="ur" dir="rtl">', self.client.get('/').text)

    def test_whatsapp_draft_follows_locale_and_keeps_identity(self):
        message = parse_qs(urlsplit(self.client.get('/product/1/ask?lang=ur&topic=fit&size=M').location).query)['text'][0]
        self.assertIn('السلام علیکم', message)
        self.assertIn('Mehr · Emerald', message)
        self.assertIn('1', message)
        self.assertIn('M', message)
        self.assertNotIn('Could you help me', message)
