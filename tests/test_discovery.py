"""Research-led catalog additions preserve truthful facts and order boundaries."""
import json
import re
import sqlite3
import unittest
from html import unescape
import test_shop
from catalog import empty_details

class DiscoveryTests(unittest.TestCase):
    setUp = test_shop.ShopTests.setUp
    tearDown = test_shop.ShopTests.tearDown
    post = test_shop.ShopTests.post
    login = test_shop.ShopTests.login
    quote = test_shop.ShopTests.quote
    order_fields = test_shop.ShopTests.order_fields

    def facts(self, pid=1, **changes):
        value = dict(empty_details(), **changes)
        with sqlite3.connect(self.database) as db:
            db.execute('INSERT INTO product_details VALUES(?,?) ON CONFLICT(product_id) DO UPDATE SET data=excluded.data', (pid,json.dumps(value)))
        return value

    def edit_fields(self, pid=1, **changes):
        html=self.client.get('/admin/product/'+str(pid)).get_data(as_text=True)
        version=unescape(re.search('name="edit_version" value="([^"]+)"',html).group(1))
        return dict(name='Measured piece',category='Stitched / Pret',price=6490,fabric='Cotton',description='Actual listing',sizes=['M'],images='https://example.com/garment.jpg',stock_M=10,active='on',edit_version=version,**changes)

    def test_combined_filters_and_current_size_inventory(self):
        self.facts(occasion='unused',occasions=['everyday'],fabric_family='Lawn')
        self.facts(2,occasions=['everyday'],fabric_family='Lawn')
        html=self.client.get('/?occasion=everyday&fabric_family=Lawn&size=M&budget=6500&sort=price-low').get_data(as_text=True)
        self.assertLess(html.index('Gul · Rose'),html.index('Mehr · Emerald'))
        self.assertNotIn('Noor · Midnight',html)
        with sqlite3.connect(self.database) as db:
            db.execute("UPDATE inventory SET quantity=0 WHERE product_id=1 AND size='M'")
            db.execute('UPDATE products SET sizes=? WHERE id=2',(json.dumps(['S']),))
        html=self.client.get('/?occasion=everyday&fabric_family=Lawn&size=M').get_data(as_text=True)
        self.assertNotIn('Mehr · Emerald',html)
        self.assertNotIn('Gul · Rose',html)
        self.assertIn('No pieces match',html)
        self.assertIn('Neel · Indigo',self.client.get('/?q=photo').get_data(as_text=True))
        for budget in ('-1','NaN','1e4','99999999999999999999','١٠'):
            self.assertEqual(self.client.get('/?budget='+budget).status_code,400)
        self.assertEqual(self.client.get('/?occasion=anything&size=bad&fabric_family=bad').status_code,200)

    def test_facts_editor_persists_validates_and_escapes(self):
        self.login()
        fields=self.edit_fields(detail_included='Shirt only <script>alert(1)</script>',detail_composition='100% cotton',detail_fabric_family='Cotton',detail_occasions=['everyday'],measure_M_chest='20.25',measure_M_length='42',measure_S_chest='18')
        self.assertEqual(self.post('/admin/product/1',fields).status_code,303)
        with sqlite3.connect(self.database) as db:
            data=json.loads(db.execute('SELECT data FROM product_details WHERE product_id=1').fetchone()[0])
        self.assertEqual(data['measurements'],{'M':{'chest':20.25,'hip':None,'length':42.0,'sleeve':None}})
        html=self.client.get('/product/1').get_data(as_text=True)
        self.assertIn('&lt;script&gt;',html)
        self.assertNotIn('<script>alert',html)
        self.assertIn('data-inches="20.25"',html)
        for bad in ('nan','inf','-1','0','0.001','151'):
            invalid=self.edit_fields(measure_M_chest=bad)
            response=self.post('/admin/product/1',invalid)
            self.assertEqual(response.status_code,200)
            self.assertIn('Measurements must',response.get_data(as_text=True))
        with sqlite3.connect(self.database) as db:
            self.assertEqual(json.loads(db.execute('SELECT data FROM product_details WHERE product_id=1').fetchone()[0]),data)
        self.assertEqual(self.post('/admin/product/1/delete').status_code,303)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM product_details').fetchone()[0],0)

    def test_facts_are_part_of_stale_editor_check(self):
        self.login();fields=self.edit_fields()
        self.facts(included='Updated by another editor')
        self.assertEqual(self.post('/admin/product/1',fields).status_code,409)

    def test_new_facts_require_review_and_receipt_keeps_snapshot(self):
        self.facts(included='Shirt and dupatta',measurements={'M':{'chest':20,'length':42}})
        self.post('/cart',dict(id=1,size='M',quantity=1))
        fields=self.order_fields()
        self.facts(included='Shirt, trousers and dupatta',measurements={'M':{'chest':21,'length':42}})
        self.assertEqual(self.post('/checkout',fields).status_code,409)
        response=self.post('/checkout',self.order_fields())
        self.assertEqual(response.status_code,303)
        self.facts(included='Changed after order')
        receipt=self.client.get(response.location).get_data(as_text=True)
        self.assertIn('Shirt, trousers and dupatta',receipt)
        self.assertNotIn('Changed after order',receipt)
        self.assertIn('Chest width: 21',receipt)

    def test_legacy_products_and_unstitched_have_no_invented_chart(self):
        html=self.client.get('/product/1').get_data(as_text=True)
        self.assertIn('Measurements have not been added',html)
        self.assertNotIn('data-inches=',html)
        with sqlite3.connect(self.database) as db:
            db.execute('UPDATE products SET sizes=? WHERE id=2',(json.dumps(['Custom Unstitched']),))
        self.facts(2,fabric_lengths='Shirt 2.5 m × 1.1 m')
        html=self.client.get('/product/2').get_data(as_text=True)
        self.assertIn('Shirt 2.5 m × 1.1 m',html)
        self.assertNotIn('data-inches=',html)
        for path in ('/our-roots','/fabric-and-fit'):
            self.assertEqual(self.client.get(path).status_code,200)

    def test_seller_health_is_private_and_flags_missing_fields(self):
        self.assertEqual(self.client.get('/admin/insights').status_code,302)
        self.login()
        html=self.client.get('/admin/insights').get_data(as_text=True)
        self.assertIn('0 / 8',html)
        self.assertIn('included pieces',html)
        self.assertIn('Not profit',html)

    def test_shared_phone_forget_revokes_access_without_cancelling_order(self):
        self.post('/cart',dict(id=1,size='M',quantity=1))
        receipt=self.post('/checkout',self.order_fields()).location
        self.assertEqual(self.client.get(receipt).status_code,200)
        self.assertEqual(self.client.post('/orders/forget').status_code,400)
        self.assertEqual(self.post('/orders/forget').status_code,303)
        self.assertEqual(self.client.get(receipt).status_code,404)
        self.assertNotIn('View summary',self.client.get('/orders').get_data(as_text=True))
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT status FROM orders').fetchone()[0],'pending')
            self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0],19)
