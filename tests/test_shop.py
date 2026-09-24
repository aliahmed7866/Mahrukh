import importlib.util
import json
from pathlib import Path
import sqlite3
import os
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app
from register import merge_registry


class ShopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.database = str(Path(self.tmp.name) / 'test.sqlite3')
        self.app = create_app(dict(TESTING=True, SECRET_KEY='test-secret', DATABASE=self.database,
                 ADMIN_HASH=generate_password_hash('long-test-password', method='pbkdf2:sha256'), SELLER_PHONE='923001234567'))
        with sqlite3.connect(self.database) as connection:
            fixtures = [('Mehr · Emerald','Stitched / Pret',6490), ('Gul · Rose','Unstitched',4290),
                        ('Noor · Midnight','Abayas',7990), ('Surkh','Festive Wear',15900),
                        ('Chand','Luxury Formals',18900), ('Neel · Indigo','Stitched / Pret',5990),
                        ('Mehfil','Festive Wear',12900), ('Shaam','Luxury Formals',16900)]
            for name, category, price in fixtures:
                connection.execute('INSERT INTO products(name,category,price,fabric,description,sizes,images,illustration) VALUES(?,?,?,?,?,?,?,0)',
                    (name,category,price,'Cotton','Photo fixture',json.dumps(['S','M','L','XL']),json.dumps(['https://example.com/product.jpg'])))
        self.client = self.app.test_client()
        self.client.get('/')

    def tearDown(self):
        self.tmp.cleanup()

    def post(self, route, data=None, **kwargs):
        with self.client.session_transaction() as session:
            session.setdefault('csrf', 'test-token')
            token = session['csrf']
        return self.client.post(route, data={**(data or {}), 'csrf_token': token}, **kwargs)

    def login(self):
        return self.post('/admin/login', {'password': 'long-test-password'})

    def test_catalog_filters_and_all_art(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        for path in (ROOT / 'static/art').glob('*.svg'):
            with self.client.get('/static/art/' + path.name) as response:
                self.assertEqual(response.status_code, 200)
        text = self.client.get('/?category=Abayas').get_data(as_text=True)
        self.assertIn('Noor · Midnight', text)
        self.assertNotIn('Mehr · Emerald', text)
        text = self.client.get('/?q=Indigo').get_data(as_text=True)
        self.assertIn('Neel · Indigo', text)
        self.assertNotIn('Mehr · Emerald', text)
        self.assertEqual(self.client.get('/product/1').status_code, 200)
        self.assertEqual(self.client.get('/product/999').status_code, 404)

    def test_cart_checkout_recomputes_prices_and_encodes_message(self):
        self.assertEqual(self.post('/cart', dict(id=1, size='M', quantity=2, price=1)).status_code, 303)
        with sqlite3.connect(self.database) as db:
            db.execute('UPDATE products SET price=7000 WHERE id=1')
        response = self.post('/checkout', dict(name='A & B', city='Lahore', contact='03001234567', address='Street #2'))
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.location.startswith('https://wa.me/923001234567?text='))
        decoded = unquote(response.location)
        self.assertIn('Items total: PKR 14,000', decoded)
        self.assertIn('Qty 2', decoded)
        self.assertIn('A & B', decoded)
        self.assertIn('Street #2', decoded)
        self.assertEqual(self.post('/cart', dict(id=1, size='M', quantity=0, action='update')).status_code, 303)
        self.assertEqual(self.post('/checkout').status_code, 400)

    def test_bad_cart_and_csrf(self):
        self.assertEqual(self.client.post('/cart', data=dict(id=1, size='M')).status_code, 400)
        for fields in [dict(id=1,size='unknown',quantity=1), dict(id=1,size='M',quantity=-1), dict(id=1,size='M',quantity=11)]:
            self.assertEqual(self.post('/cart', fields).status_code, 400)
        self.post('/cart', dict(id=1,size='M',quantity=10))
        self.assertEqual(self.post('/cart', dict(id=1,size='M',quantity=1)).status_code, 400)

    def test_drawer_and_cookie_isolation(self):
        response = self.post('/cart', dict(id=1, size='S', quantity=1), headers={'X-Mahrukh-Drawer':'1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Cart-Count'], '1')
        self.assertNotIn('<html', response.get_data(as_text=True))
        self.assertIn('mahrukh_session=', response.headers['Set-Cookie'])

    def test_hidden_deleted_and_changed_sizes_removed_from_cart(self):
        self.post('/cart', dict(id=1, size='M', quantity=1))
        with sqlite3.connect(self.database) as db:
            db.execute('UPDATE products SET active=0 WHERE id=1')
        self.assertIn('currently empty', self.client.get('/cart').get_data(as_text=True))
        self.assertEqual(self.client.get('/product/1').status_code, 404)

    def test_admin_crud_requires_login_and_validates(self):
        self.assertEqual(self.client.get('/admin').status_code, 302)
        self.assertEqual(self.post('/admin/product/1/delete').status_code, 302)
        self.assertEqual(self.login().status_code, 303)
        self.assertEqual(self.client.get('/admin').status_code, 200)
        self.client.get('/admin/product/new')
        fields = dict(name='Test piece', category='Abayas',price=3000,compare_price=4000,
                      fabric='Cotton',description='Test',sizes=['M'],images='https://example.com/abaya.jpg',active='on')
        self.assertEqual(self.post('/admin/product/new', fields).status_code, 303)
        fields['name']='Edited piece'
        self.assertEqual(self.post('/admin/product/9', fields).status_code, 303)
        self.assertIn('Edited piece', self.client.get('/product/9').get_data(as_text=True))
        fields['images']='javascript:alert(1)'
        response=self.post('/admin/product/9',fields)
        self.assertIn('HTTPS product image',response.get_data(as_text=True))
        self.assertEqual(self.post('/admin/product/9/delete').status_code,303)
        self.assertEqual(self.client.get('/product/9').status_code,404)
        self.post('/admin/logout')
        self.assertEqual(self.client.get('/admin').status_code,302)

    def test_admin_throttle(self):
        for _ in range(5):
            self.post('/admin/login', {'password':'wrong'})
        self.assertEqual(self.login().status_code,429)

    def test_disabled_checkout(self):
        self.app.config['SELLER_PHONE']=''
        self.post('/cart',dict(id=1,size='S',quantity=1))
        self.assertEqual(self.post('/checkout').status_code,503)

    def test_brand_art_is_separate_from_product_photographs(self):
        html = self.client.get('/').get_data(as_text=True)
        self.assertIn('art/heritage-woman.svg', html)
        self.assertIn('art/festive-woman.svg', html)
        detail = self.client.get('/product/1').get_data(as_text=True)
        self.assertIn('https://example.com/product.jpg', detail)
        self.assertNotIn('/static/art/', detail)
        self.login()
        fields = dict(name='Wrong artwork', category='Abayas', price=3000, fabric='Cotton',
                      sizes=['M'], images='/static/art/heritage-woman.svg', active='on')
        response = self.post('/admin/product/new', fields)
        self.assertIn('actual photograph', response.get_data(as_text=True))
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM products').fetchone()[0], 8)

    def test_upgrade_hides_art_samples_but_preserves_real_products(self):
        with sqlite3.connect(self.database) as db:
            db.execute('UPDATE products SET images=? WHERE id=1', (json.dumps(['/static/art/emerald-pret.svg']),))
        upgraded = create_app(dict(TESTING=True, SECRET_KEY='test-secret', DATABASE=self.database,
                                  ADMIN_HASH='existing-hash'))
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT active FROM products WHERE id=1').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT active FROM products WHERE id=2').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT count(*) FROM products').fetchone()[0], 8)
        self.assertEqual(upgraded.test_client().get('/product/1').status_code, 404)

    def test_new_database_has_no_sample_inventory(self):
        fresh = str(Path(self.tmp.name) / 'fresh.sqlite3')
        create_app(dict(TESTING=True, SECRET_KEY='test-secret', DATABASE=fresh, ADMIN_HASH='existing-hash'))
        with sqlite3.connect(fresh) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM products').fetchone()[0], 0)

    def test_standalone_registration_does_not_create_hub(self):
        folder = Path(self.tmp.name)
        (folder / 'config.json').write_text(json.dumps({'port': 5050}))
        registry = folder / 'missing-hub' / 'apps.json'
        env = {**os.environ, 'MAHRUKH_INSTANCE': str(folder), 'AYCF_ADMIN_REGISTRY': str(registry)}
        result = subprocess.run([sys.executable, str(ROOT / 'register.py')], env=env,
                                capture_output=True, text=True, check=True)
        self.assertIn('standalone setup continues', result.stdout)
        self.assertFalse(registry.exists())

    def test_registry_preserves_apps_and_rejects_collision(self):
        target=Path(self.tmp.name)/'apps.json'
        custom=dict(id='aycf',port=9100,name='Custom planner',custom='keep')
        target.write_text(json.dumps({'apps':[custom], 'extra':True}))
        merge_registry(target,8085)
        payload=json.loads(target.read_text())
        self.assertEqual(payload['apps'][0],custom)
        self.assertTrue(payload['extra'])
        merge_registry(target,8086)
        self.assertEqual(len(json.loads(target.read_text())['apps']),2)
        previous=target.read_text()
        with self.assertRaises(ValueError): merge_registry(target,9100)
        self.assertEqual(target.read_text(),previous)

if __name__=='__main__': unittest.main()
