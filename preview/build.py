"""Build both languages of the non-selling preview, without reading the database."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import sys
from urllib.parse import urlencode
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'preview'
OUT = ROOT / 'preview-site'
sys.path.insert(0, str(ROOT))
from catalog import OCCASIONS, FABRICS, MEASUREMENTS, QUESTIONS
from i18n import content, localized, t, translation_catalog, use_locale

SIZES = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', 'Custom Unstitched']
CATEGORIES = ['Unstitched', 'Stitched / Pret', 'Luxury Formals', 'Abayas', 'Festive Wear']
ASSETS = ('style.css', 'heritage.css', 'business.css', 'discovery.css',
          'discovery.js', 'boutique.css', 'boutique.js', 'i18n.css', 'i18n.js')


def preview_url(endpoint, locale='en', **kwargs):
    if endpoint == 'static':
        return ('../' if locale == 'ur' else '') + 'assets/' + kwargs['filename']
    pages = {'index': 'index.html', 'contact': 'contact.html', 'saved': 'saved.html',
             'roots': 'our-roots.html', 'fit_guide': 'fabric-and-fit.html', 'studio': 'studio.html'}
    if endpoint == 'detail':
        return f"product-{kwargs['pid']}.html"
    if endpoint not in pages:
        raise ValueError('Live endpoint must not appear in preview: ' + endpoint)
    query = {key: value for key, value in kwargs.items() if key != 'lang'}
    return pages[endpoint] + ('?' + urlencode(query) if query else '')


def build():
    fixtures = json.loads((HERE / 'products.json').read_text())
    for product in fixtures:
        if not (HERE / 'photos' / product['photo']).is_file():
            raise FileNotFoundError('Missing concept photo: ' + product['photo'])
    (OUT / 'assets').mkdir(parents=True, exist_ok=True)
    # Explicit allowlist: no instance files, credentials, backend, or real inventory.
    for name in ASSETS:
        shutil.copyfile(ROOT / 'static' / name, OUT / 'assets' / name)
    shutil.copytree(ROOT / 'static/art', OUT / 'assets/art', dirs_exist_ok=True)
    shutil.copytree(HERE / 'photos', OUT / 'assets/photos', dirs_exist_ok=True)
    shutil.copytree(ROOT / 'static/fonts', OUT / 'assets/fonts', dirs_exist_ok=True)
    for name in ('preview.css', 'preview.js'):
        shutil.copyfile(HERE / name, OUT / 'assets' / name)
    for path in (OUT / 'assets').glob('*.css'):
        path.write_text(path.read_text().replace('/static/art/', 'art/'))
    asset_version = hashlib.sha256(b''.join(
        (OUT / 'assets' / name).read_bytes() for name in (*ASSETS, 'preview.css', 'preview.js')
    )).hexdigest()[:12]
    for locale in ('en', 'ur'):
        destination = OUT / 'ur' if locale == 'ur' else OUT
        destination.mkdir(exist_ok=True)
        products = copy.deepcopy(fixtures)
        for product in products:
            product['images'] = [preview_url('static', locale, filename='photos/' + product['photo'])]
        env = Environment(loader=FileSystemLoader([str(HERE / 'templates'), str(ROOT / 'templates')]),
                          autoescape=select_autoescape())
        current_page = {'name': 'index.html'}
        def language_url(code):
            if code == locale:
                return current_page['name']
            return ('../' if locale == 'ur' else 'ur/') + current_page['name']
        env.globals.update(
            url_for=lambda endpoint, **kwargs: preview_url(endpoint, locale, **kwargs),
            language_url=language_url, t=t, localized=localized, content=content,
            translation_catalog=translation_catalog, current_locale=lambda: locale,
            locale=locale, direction='rtl' if locale == 'ur' else 'ltr',
            categories=CATEGORIES, demo=True, asset_version=asset_version,
            occasions=OCCASIONS, fabrics=FABRICS, sizes=SIZES, measurement_labels=MEASUREMENTS,
            enquiry_topics=QUESTIONS, saved_ids=[], demo_product_ids=[p['id'] for p in products],
            shop=dict(personal_note='A favourite outfit has a way of finding its place in your life. Worn on a busy morning, taken out for a family gathering, reached for simply because it feels like you.\n\nTake your time here. Look at the details, explore a little, and ask the questions that matter to you. There is always room for another conversation.',
                      personal_note_ur='پسندیدہ لباس آپ کی زندگی میں اپنی جگہ بنا لیتا ہے۔ کبھی مصروف صبح میں، کبھی گھر والوں کی محفل میں، اور کبھی صرف اس لیے کہ اسے پہن کر آپ خود کو اچھا محسوس کرتی ہیں۔\n\nآرام سے دیکھیں۔ تفصیلات پڑھیں اور اپنے سوال پوچھیں۔ گفتگو کی گنجائش ہمیشہ رہتی ہے۔',
                      note_signature='With warmth, Mahrukh', note_signature_ur='خلوص کے ساتھ، Mahrukh'))
        env.filters['pkr'] = lambda value: f'PKR {value:,.0f}'
        def render(filename, template, **values):
            current_page['name'] = filename
            (destination / filename).write_text(env.get_template(template).render(**values))
        with use_locale(locale):
            render('index.html', 'index.html', products=products, query='', selected='', sort='featured',
                   filters=dict(occasion='', fabric_family='', size='', budget=''), filtered=False, chips=[])
            render('saved.html', 'saved.html', products=products, saved_page=True)
            for product in products:
                related = sorted([other for other in products if other['id'] != product['id']],
                                 key=lambda other: (other['category'] != product['category'], -other['id']))[:3]
                render(f"product-{product['id']}.html", 'demo-product.html', item=product, related=related)
            for name, template in [('our-roots', 'roots.html'), ('fabric-and-fit', 'fit_guide.html')]:
                render(name + '.html', template)
            for name in ('contact', 'studio', '404'):
                render(name + '.html', f'demo-{name}.html')
    (OUT / '.nojekyll').write_text('')
    print(f'Built {len(fixtures)} sample products in English and Urdu: {OUT}')
    return OUT


if __name__ == '__main__':
    build()
