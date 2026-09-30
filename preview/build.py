"""Build a public, non-selling design demo. Never reads the live app or database."""
from pathlib import Path
import json
import hashlib
import shutil
import sys
from urllib.parse import urlencode
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'preview'
OUT=ROOT/'preview-site'
sys.path.insert(0,str(ROOT))
from catalog import OCCASIONS, FABRICS, MEASUREMENTS, QUESTIONS
SIZES=['XS','S','M','L','XL','2XL','3XL','Custom Unstitched']
CATEGORIES=['Unstitched','Stitched / Pret','Luxury Formals','Abayas','Festive Wear']

def url_for(endpoint, **kwargs):
    if endpoint=='static': return 'assets/'+kwargs['filename']
    if endpoint=='index': return 'index.html'+('?' + urlencode(kwargs) if kwargs else '')
    if endpoint=='contact': return 'contact.html'
    if endpoint=='saved': return 'saved.html'
    if endpoint=='roots': return 'our-roots.html'
    if endpoint=='fit_guide': return 'fabric-and-fit.html'
    if endpoint=='detail': return f"product-{kwargs['pid']}.html"
    raise ValueError('Live endpoint must not appear in preview: '+endpoint)

def build():
    products=json.loads((HERE/'products.json').read_text())
    for p in products:
        if not (HERE/'photos'/p['photo']).is_file():
            raise FileNotFoundError('Missing concept photo: '+p['photo'])
        p['images']=['assets/photos/'+p['photo']]
    OUT.mkdir(exist_ok=True)
    (OUT/'assets').mkdir(exist_ok=True)
    # Explicit allowlist: no instance files, credentials, backend, or real inventory.
    for name in ('style.css','heritage.css','business.css','discovery.css','discovery.js','boutique.css','boutique.js'):
        shutil.copyfile(ROOT/'static'/name, OUT/'assets'/name)
    shutil.copytree(ROOT/'static/art',OUT/'assets/art',dirs_exist_ok=True)
    shutil.copytree(HERE/'photos',OUT/'assets/photos',dirs_exist_ok=True)
    for name in ('preview.css','preview.js'):
        shutil.copyfile(HERE/name,OUT/'assets'/name)
    # CSS paths must work at /Mahrukh/ and at a custom-domain root.
    for path in (OUT/'assets').glob('*.css'):
        path.write_text(path.read_text().replace('/static/art/','art/'))
    env=Environment(loader=FileSystemLoader([str(HERE/'templates'),str(ROOT/'templates')]),autoescape=select_autoescape())
    asset_version=hashlib.sha256(b''.join((OUT/'assets'/name).read_bytes() for name in ('preview.js','preview.css','business.css','heritage.css','style.css','discovery.css','discovery.js','boutique.css','boutique.js'))).hexdigest()[:12]
    env.globals.update(url_for=url_for,categories=CATEGORIES,demo=True,asset_version=asset_version,occasions=OCCASIONS,fabrics=FABRICS,sizes=SIZES,measurement_labels=MEASUREMENTS,enquiry_topics=QUESTIONS,saved_ids=[],demo_product_ids=[p['id'] for p in products],shop=dict(personal_note='A favourite outfit has a way of finding its place in your life. Worn on a busy morning, taken out for a family gathering, reached for simply because it feels like you.\n\nTake your time here. Look at the details, explore a little, and ask the questions that matter to you. There is always room for another conversation.',note_signature='With warmth, Mahrukh'))
    env.filters['pkr']=lambda value:f'PKR {value:,.0f}'
    (OUT/'index.html').write_text(env.get_template('index.html').render(products=products,query='',selected='',sort='featured',filters=dict(occasion='',fabric_family='',size='',budget=''),filtered=False,chips=[]))
    (OUT/'saved.html').write_text(env.get_template('saved.html').render(products=products,saved_page=True))
    for p in products:
        (OUT/f"product-{p['id']}.html").write_text(env.get_template('demo-product.html').render(item=p,related=sorted([other for other in products if other['id']!=p['id']],key=lambda other:(other['category']!=p['category'],-other['id']))[:3]))
    for name,template in [('our-roots','roots.html'),('fabric-and-fit','fit_guide.html')]:
        (OUT/f'{name}.html').write_text(env.get_template(template).render())
    for name in ('contact','studio'):
        (OUT/f'{name}.html').write_text(env.get_template(f'demo-{name}.html').render())
    (OUT/'.nojekyll').write_text('')
    (OUT/'404.html').write_text(env.get_template('demo-404.html').render())
    print(f'Built {len(products)} sample product pages and homepage in {OUT}')

if __name__=='__main__': build()
