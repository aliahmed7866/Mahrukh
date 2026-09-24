"""Build a public, non-selling design demo. Never reads the live app or database."""
from pathlib import Path
import json
import shutil
from urllib.parse import urlencode
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'preview'
OUT=ROOT/'preview-site'
CATEGORIES=['Unstitched','Stitched / Pret','Luxury Formals','Abayas','Festive Wear']

def url_for(endpoint, **kwargs):
    if endpoint=='static': return 'assets/'+kwargs['filename']
    if endpoint=='index': return 'index.html'+('?' + urlencode(kwargs) if kwargs else '')
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
    for name in ('style.css','heritage.css'):
        shutil.copyfile(ROOT/'static'/name, OUT/'assets'/name)
    shutil.copytree(ROOT/'static/art',OUT/'assets/art',dirs_exist_ok=True)
    shutil.copytree(HERE/'photos',OUT/'assets/photos',dirs_exist_ok=True)
    for name in ('preview.css','preview.js'):
        shutil.copyfile(HERE/name,OUT/'assets'/name)
    # CSS paths must work at /Mahrukh/ and at a custom-domain root.
    for path in (OUT/'assets').glob('*.css'):
        path.write_text(path.read_text().replace('/static/art/','art/'))
    env=Environment(loader=FileSystemLoader([str(HERE/'templates'),str(ROOT/'templates')]),autoescape=select_autoescape())
    env.globals.update(url_for=url_for,categories=CATEGORIES)
    env.filters['pkr']=lambda value:f'PKR {value:,.0f}'
    page=(ROOT/'templates/index.html').read_text()
    page=page.replace('Order with WhatsApp', 'Explore the design')
    page=page.replace('<article class="product-card">','<article class="product-card" data-name="{{ p.name }} {{ p.fabric }}" data-category="{{ p.category }}" data-price="{{ p.price }}">')
    page=page.replace('{{ products|length }} pieces','<span id="result-count">{{ products|length }}</span> sample pieces')
    page=page.replace('<h2>{{ selected or', '<h2 id="collection-title">{{ selected or')
    page=page.replace('<p>{{ p.price|pkr }}','<p><span class="sample-price">Sample price</span>{{ p.price|pkr }}')
    page=page.replace('<div class="product-info">','<div class="product-info"><span class="concept-label">AI-generated concept · Not for sale</span>')
    page=page.replace('<div class="product-grid">','<p id="no-results" class="notice" hidden>No samples match your search. Try another category or search term.</p><div class="product-grid">')
    (OUT/'index.html').write_text(env.from_string(page).render(products=products,query='',selected='',sort='featured'))
    for p in products:
        (OUT/f"product-{p['id']}.html").write_text(env.get_template('demo-product.html').render(item=p))
    (OUT/'.nojekyll').write_text('')
    (OUT/'404.html').write_text(env.get_template('demo-404.html').render())
    print(f'Built {len(products)} sample product pages and homepage in {OUT}')

if __name__=='__main__': build()
