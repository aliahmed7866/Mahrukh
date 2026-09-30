import json
import sqlite3
import unittest
from urllib.parse import parse_qs, urlsplit
from html.parser import HTMLParser
import test_shop
from commerce import DEFAULTS, validate_settings

class BoutiqueTests(unittest.TestCase):
    setUp=test_shop.ShopTests.setUp
    tearDown=test_shop.ShopTests.tearDown
    post=test_shop.ShopTests.post
    login=test_shop.ShopTests.login

    def test_saved_actions_are_private_idempotent_and_do_not_reserve_stock(self):
        self.assertEqual(self.client.post('/saved/1',data={'action':'save'}).status_code,400)
        for _ in range(2):
            response=self.post('/saved/1',{'action':'save'},headers={'X-Mahrukh-Saved':'1'})
            self.assertEqual(response.json,{'saved':True,'count':1})
        self.assertIn('Mehr · Emerald',self.client.get('/saved').get_data(as_text=True))
        self.assertNotIn('Mehr · Emerald',self.app.test_client().get('/saved').get_data(as_text=True))
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute("SELECT quantity FROM inventory WHERE product_id=1 AND size='M'").fetchone()[0],20)
        self.login()
        self.assertIn('Mehr · Emerald',self.client.get('/saved').get_data(as_text=True))
        self.post('/admin/logout')
        response=self.post('/saved/1',{'action':'remove'},headers={'X-Mahrukh-Saved':'1'})
        self.assertEqual(response.json,{'saved':False,'count':0})
        self.assertEqual(self.post('/saved/1',{'action':'unexpected'}).status_code,400)

    def test_saved_collection_bounds_and_unavailable_cleanup(self):
        with sqlite3.connect(self.database) as db:
            for number in range(9,26):
                db.execute("INSERT INTO products(name,category,price,fabric,description,sizes,images) VALUES(?,?,?,?,?,?,?)",(f'Extra {number}','Abayas',2000,'Cotton','Fixture','["M"]','["https://example.com/product.jpg"]'))
        with self.client.session_transaction() as state: state['saved']=list(range(1,25))
        self.assertEqual(self.post('/saved/25',{'action':'save'}).status_code,409)
        with sqlite3.connect(self.database) as db: db.execute('UPDATE products SET active=0 WHERE id=1')
        self.assertEqual(self.post('/saved/1',{'action':'save'}).status_code,404)
        self.assertEqual(self.post('/saved/25',{'action':'save'}).status_code,303)
        self.assertNotIn('Mehr · Emerald',self.client.get('/saved').get_data(as_text=True))
        self.assertEqual(self.post('/saved/clear').status_code,303)
        self.assertIn('A little space for your favourites',self.client.get('/saved').get_data(as_text=True))

    def test_save_return_paths_never_redirect_offsite(self):
        for target in ('https://evil.example','//evil.example','https://[','/\\evil.example','/admin','javascript:alert(1)'):
            with self.subTest(target=target):
                response=self.post('/saved/1',{'action':'save','return_to':target})
                self.assertEqual(response.status_code,303)
                self.assertEqual(response.location,'/saved')
        target='/?category=Abayas&size=M#collection'
        self.assertEqual(self.post('/saved/1',{'action':'save','return_to':target}).location,target)

    def test_whatsapp_question_is_encoded_validated_and_not_sent(self):
        response=self.client.get('/product/1/ask?topic=fit&size=M')
        self.assertEqual(response.status_code,302)
        url=urlsplit(response.location)
        self.assertEqual((url.scheme,url.netloc,url.path),('https','wa.me','/923001234567'))
        text=parse_qs(url.query)['text'][0]
        self.assertIn('Mehr · Emerald',text)
        self.assertIn('Size I am considering: M',text)
        self.assertIn('confirm the measurements',text)
        self.assertEqual(self.client.get('/product/1/ask?topic=unknown').status_code,400)
        self.assertEqual(self.client.get('/product/1/ask?size=XS').status_code,400)
        with sqlite3.connect(self.database) as db:
            data=json.loads(db.execute('SELECT data FROM shop_settings').fetchone()[0]);data['whatsapp']=''
            db.execute('UPDATE shop_settings SET data=?',(json.dumps(data),))
        self.assertEqual(self.client.get('/product/1/ask').location,'/contact')

    def test_seller_note_is_opt_in_escaped_and_limited(self):
        self.assertNotIn('A NOTE FROM MAHRUKH',self.client.get('/').get_data(as_text=True))
        self.login()
        with sqlite3.connect(self.database) as db: fields=json.loads(db.execute('SELECT data FROM shop_settings').fetchone()[0])
        fields={key:value for key,value in fields.items() if value is not False}
        fields.update(personal_note='Welcome <script>alert(1)</script>\nFrom my wardrobe to yours.',note_signature='Mahrukh',support_languages='Urdu & English')
        self.assertEqual(self.post('/admin/settings',fields).status_code,303)
        html=self.client.get('/').get_data(as_text=True)
        self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>alert',html)
        self.assertIn('Happy to help in Urdu &amp; English',self.client.get('/contact').get_data(as_text=True))
        for key,value in [('personal_note','x'*801),('note_signature','x'*81),('support_languages','x'*121)]:
            with self.assertRaises(ValueError): validate_settings(dict(fields,**{key:value}))

    def test_related_pieces_exclude_hidden_and_sold_out_purchase_is_disabled(self):
        with sqlite3.connect(self.database) as db:
            db.execute('UPDATE products SET active=0 WHERE id=6')
            db.execute('UPDATE inventory SET quantity=0 WHERE product_id=1')
        html=self.client.get('/product/1').get_data(as_text=True)
        self.assertIn('Currently sold out',html)
        self.assertNotIn('Neel · Indigo',html)
        self.assertIn('You might also be drawn to',html)
        class Buttons(HTMLParser):
            def __init__(self): super().__init__();self.disabled=[]
            def handle_starttag(self,tag,attrs):
                if tag=='button' and 'disabled' in dict(attrs): self.disabled.append(attrs)
        parser=Buttons();parser.feed(html);self.assertTrue(parser.disabled)

    def test_filter_chip_removes_only_its_own_filter(self):
        html=self.client.get('/?q=Cotton&category=Abayas&size=M&budget=8000&sort=price-low').get_data(as_text=True)
        class Links(HTMLParser):
            def __init__(self): super().__init__();self.removal=None
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if tag=='a' and a.get('aria-label')=='Remove filter M': self.removal=a['href']
        links=Links();links.feed(html)
        params=parse_qs(urlsplit(links.removal).query)
        self.assertNotIn('size',params)
        self.assertEqual(params,{'q':['Cotton'],'category':['Abayas'],'budget':['8000'],'sort':['price-low']})
