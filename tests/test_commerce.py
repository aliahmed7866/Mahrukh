import concurrent.futures
import io
import json
import re
import sqlite3
import threading
import unittest
from html import unescape
import test_shop
from commerce import DEFAULTS, validate_settings, safe_url

class CommerceTests(unittest.TestCase):
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
            db.execute('UPDATE shop_settings SET data=?',(json.dumps(data),))
        return data

    def place(self, **changes):
        self.post('/cart',dict(id=1,size='M',quantity=1))
        response = self.post('/checkout',{**self.order_fields(),**changes})
        self.assertEqual(response.status_code,303,response.get_data(as_text=True))
        return response.location.rsplit('/',1)[-1]

    def manage(self, ref, **changes):
        html = self.client.get('/admin/order/'+ref).get_data(as_text=True)
        version = re.search('name="version" value="([^"]+)"',html).group(1)
        return self.post('/admin/order/'+ref,dict(version=version,status='confirmed',payment_status='unpaid',**changes))

    def test_settings_auth_validation_and_immediate_public_links(self):
        self.assertEqual(self.client.get('/admin/settings').status_code,302)
        self.login()
        fields = self.setting(instagram='https://www.instagram.com/mahrukh',support_hours='10am–6pm PKT')
        fields = {k:('on' if v is True else str(v)) for k,v in fields.items() if v is not False}
        self.assertEqual(self.post('/admin/settings',fields).status_code,303)
        self.assertIn('https://www.instagram.com/mahrukh',self.client.get('/').get_data(as_text=True))
        self.assertIn('10am–6pm PKT',self.client.get('/contact').get_data(as_text=True))
        fields['instagram']='https://instagram.com.attacker.test/profile'
        self.assertIn('official domain', self.post('/admin/settings',fields).get_data(as_text=True))
        self.assertNotIn('attacker',self.client.get('/').get_data(as_text=True))
        fields['instagram']='https://instagram.com/good';fields['terms']=''
        self.assertIn('Before opening orders',self.post('/admin/settings',fields).get_data(as_text=True))
        self.assertEqual(self.client.get('/policies/unknown').status_code,404)

    def test_malicious_links_and_unapproved_payments_rejected(self):
        for url in ('javascript:alert(1)','http://paypal.com','https://paypal.com.evil.test','https://evil.test@paypal.com','https://paypal.com:8443/x','https://paypal.com\n.evil.test'):
            self.assertFalse(safe_url(url,('paypal.com',)),url)
        for url in ('https://paypal.com/invoice/p/123','https://www.paypal.com/invoice/123'):
            self.assertTrue(safe_url(url,('paypal.com',)))
        with self.assertRaises(ValueError): validate_settings(dict(hosted='on',provider='safepay'))

    def test_delivery_free_threshold_consent_and_city(self):
        self.setting(free_shipping_at=6000)
        self.post('/cart',dict(id=1,size='M',quantity=1))
        fields=self.order_fields()
        self.assertEqual(self.post('/checkout',{**fields,'agree':''}).status_code,400)
        self.assertEqual(self.post('/checkout',{**fields,'city':'unsupported'}).status_code,400)
        self.assertEqual(self.post('/checkout',{**fields,'payment_method':'hosted'}).status_code,400)
        response=self.post('/checkout',fields)
        self.assertEqual(response.status_code,303)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT total,shipping FROM orders').fetchone(),(6490,0))

    def test_stock_conflict_rolls_back_every_line(self):
        self.post('/cart',dict(id=1,size='M',quantity=1))
        self.post('/cart',dict(id=2,size='M',quantity=1))
        fields=self.order_fields()
        with sqlite3.connect(self.database) as db: db.execute("UPDATE inventory SET quantity=0 WHERE product_id=2 AND size='M'")
        self.assertEqual(self.post('/checkout',fields).status_code,409)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0],20)
            self.assertEqual(db.execute('SELECT count(*) FROM orders').fetchone()[0],0)

    def test_cancel_returns_stock_once_and_preserves_receipt(self):
        ref=self.place()
        self.login()
        html=self.client.get('/admin/order/'+ref).get_data(as_text=True)
        version=re.search('name="version" value="([^"]+)"',html).group(1)
        fields=dict(version=version,status='cancelled',payment_status='unpaid')
        self.assertEqual(self.post('/admin/order/'+ref,fields).status_code,303)
        self.assertEqual(self.post('/admin/order/'+ref,fields).status_code,409)
        fields['version']='2'
        self.assertEqual(self.post('/admin/order/'+ref,fields).status_code,303)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0],20)
        self.post('/admin/product/1/delete')
        self.assertIn('Mehr · Emerald',self.client.get('/order/'+ref).get_data(as_text=True))

    def test_payment_link_is_order_specific_and_never_auto_paid(self):
        self.setting(hosted=True, merchant_eligible=True, provider='safepay')
        ref=self.place(payment_method='hosted')
        self.login()
        self.assertIn('selected provider',self.manage(ref,payment_url='https://evil.test/pay',link_verified='yes').get_data(as_text=True))
        self.assertEqual(self.manage(ref,payment_url='https://getsafepay.com/invoice/example',link_verified='yes').status_code,303)
        self.assertIn('Open secure provider invoice',self.client.get('/order/'+ref+'?paid=true').get_data(as_text=True))
        with sqlite3.connect(self.database) as db: self.assertEqual(db.execute('SELECT payment_status FROM orders').fetchone()[0],'unpaid')
        version='2'
        bad=dict(version=version,status='dispatched',payment_status='unpaid')
        self.assertIn('Verify payment before dispatch',self.post('/admin/order/'+ref,bad).get_data(as_text=True))
        paid=dict(version=version,status='confirmed',payment_status='paid',payment_reference='Verified bank transaction 123')
        self.assertEqual(self.post('/admin/order/'+ref,paid).status_code,303)
        self.assertNotIn('Open secure provider invoice',self.client.get('/order/'+ref).get_data(as_text=True))

    def test_order_privacy_headers_and_snapshots(self):
        ref=self.place()
        self.setting(terms='Changed terms', business_name='Changed name')
        page=self.client.get('/order/'+ref)
        self.assertIn('Test terms',page.get_data(as_text=True))
        self.assertIn('Seller: Test shop',page.get_data(as_text=True))
        self.assertEqual(page.headers['Cache-Control'],'no-store')
        self.assertEqual(page.headers['Referrer-Policy'],'no-referrer')
        self.assertEqual(self.app.test_client().get('/order/'+ref).status_code,404)
        self.assertNotIn('Street #2', self.client.get('/').get_data(as_text=True))
        self.assertIn('script-src',page.headers['Content-Security-Policy'])

    def test_stale_product_edit_cannot_overwrite_reserved_stock(self):
        self.login()
        html=self.client.get('/admin/product/1').get_data(as_text=True)
        version=re.search('name="edit_version" value="([^"]+)"',html).group(1)
        with sqlite3.connect(self.database) as db: db.execute("UPDATE inventory SET quantity=19 WHERE product_id=1 AND size='M'")
        fields=dict(name='Test',category='Abayas',price=3000,fabric='Cotton',sizes=['M'],images='https://example.com/a.jpg',stock_M=20,edit_version=version)
        self.assertEqual(self.post('/admin/product/1',fields).status_code,409)
        with sqlite3.connect(self.database) as db: self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0],19)

    def test_phone_photo_upload_and_svg_rejection(self):
        self.login()
        fields=dict(name='Photo test',category='Abayas',price=3000,fabric='Cotton',sizes=['M'],stock_M=3,active='on')
        svg=self.post('/admin/product/new',{**fields,'photos':(io.BytesIO(b'<svg><script/></svg>'),'photo.svg')})
        self.assertIn('Upload JPG, PNG or WebP',svg.get_data(as_text=True))
        # Tiny real PNG fixture.
        import base64
        png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
        response=self.post('/admin/product/new',{**fields,'photos':(io.BytesIO(png),'camera.png')})
        self.assertEqual(response.status_code,303)
        with sqlite3.connect(self.database) as db: path=json.loads(db.execute('SELECT images FROM products WHERE id=9').fetchone()[0])[0]
        with self.client.get(path) as image:
            self.assertEqual(image.status_code,200)
            self.assertEqual(image.mimetype,'image/png')
        self.assertEqual(self.client.get('/media/config.json').status_code,404)

    def test_simultaneous_last_item_and_duplicate_post(self):
        with sqlite3.connect(self.database) as db: db.execute("UPDATE inventory SET quantity=1 WHERE product_id=1 AND size='M'")
        clients=[]
        for _ in range(2):
            c=self.app.test_client();c.get('/')
            with c.session_transaction() as s:
                s.setdefault('csrf','concurrent-test-csrf');csrf=s['csrf']
            c.post('/cart',data=dict(csrf_token=csrf,id=1,size='M',quantity=1))
            html=c.get('/cart').get_data(as_text=True)
            fields={k:unescape(re.search('name="'+k+'" value="([^"]+)"',html).group(1)) for k in ('checkout_token','quote_hash')}
            fields.update(csrf_token=csrf,name='Test',city='Lahore',contact='03001234567',address='Test address',payment_method='cod',agree='yes')
            clients.append((c,fields))
        barrier=threading.Barrier(2)
        def submit(pair):
            barrier.wait()
            return pair[0].post('/checkout',data=pair[1])
        with concurrent.futures.ThreadPoolExecutor(2) as pool: results=list(pool.map(submit,clients))
        self.assertEqual(sorted(r.status_code for r in results),[303,409])
        winner=clients[next(i for i,r in enumerate(results) if r.status_code==303)]
        again=winner[0].post('/checkout',data=winner[1])
        self.assertEqual(again.status_code,303)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM orders').fetchone()[0],1)
            self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0],0)

    def test_paypal_requires_explicit_foreign_currency_quote(self):
        self.setting(hosted=True,merchant_eligible=True,provider='paypal')
        ref=self.place(payment_method='hosted')
        self.login()
        fields=dict(version='1',status='confirmed',payment_status='unpaid',payment_url='https://www.paypal.com/invoice/p/test',link_verified='yes')
        self.assertIn('agreed USD, GBP or EUR',self.post('/admin/order/'+ref,fields).get_data(as_text=True))
        fields.update(invoice_currency='USD',invoice_amount='24.50',quote_agreed='yes')
        self.assertEqual(self.post('/admin/order/'+ref,fields).status_code,303)
        self.assertIn('USD 24.50',self.client.get('/order/'+ref).get_data(as_text=True))
        self.assertIn('PKR 6,740',self.client.get('/order/'+ref).get_data(as_text=True))

    def test_refund_can_be_recorded_after_completion(self):
        ref=self.place()
        self.login()
        for version,status,payment in [('1','confirmed','paid'),('2','dispatched','paid'),('3','completed','paid'),('4','completed','refunded')]:
            response=self.post('/admin/order/'+ref,dict(version=version,status=status,payment_status=payment,payment_reference='Verified '+payment+' reference'))
            self.assertEqual(response.status_code,303,response.get_data(as_text=True))
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT payment_status FROM orders').fetchone()[0],'refunded')

    def test_backup_and_redaction_dry_run_use_only_private_instance(self):
        from maintenance import backup, redact
        from pathlib import Path
        import tarfile
        ref=self.place()
        with sqlite3.connect(self.database) as db:
            db.execute("UPDATE orders SET status='cancelled',updated_at='2000-01-01T00:00:00+00:00'")
        folder=Path(self.tmp.name)
        # Maintenance operates on the named production database inside the selected instance.
        source=folder/'mahrukh.sqlite3'
        with sqlite3.connect(self.database) as src, sqlite3.connect(source) as dst: src.backup(dst)
        target=backup(folder)
        with tarfile.open(target) as archive: self.assertIn('mahrukh.sqlite3',archive.getnames())
        self.assertEqual(redact(folder,365),1)
        with sqlite3.connect(source) as db: self.assertEqual(db.execute('SELECT name FROM orders').fetchone()[0],'A & B')
        self.assertEqual(redact(folder,365,True),1)
        with sqlite3.connect(source) as db: self.assertEqual(db.execute('SELECT name,contact,address,owner,total FROM orders').fetchone(),('[redacted]','','','',6740))
        self.assertEqual(redact(folder,365,True),0)

if __name__=='__main__': unittest.main()
