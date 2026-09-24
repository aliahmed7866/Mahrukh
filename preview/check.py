"""Validate generated static links and the no-transactions boundary."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
from build import OUT, build

class Links(HTMLParser):
    def __init__(self): super().__init__();self.refs=[];self.posts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        for key in ('href','src','action'):
            if a.get(key):self.refs.append(a[key])
        if tag=='form' and a.get('method','get').lower()!='get':self.posts.append(a)

build()
for file in OUT.glob('*.html'):
    text=file.read_text(); parser=Links();parser.feed(text)
    assert 'DESIGN PREVIEW' in text and not parser.posts
    assert not re.search(r'wa\.me|/checkout|/admin|csrf_token|seller_phone|admin_hash',text)
    for ref in parser.refs:
        parsed=urlsplit(ref)
        if parsed.scheme or not parsed.path:continue
        assert not parsed.path.startswith('/'),(file,ref)
        assert (file.parent/unquote(parsed.path)).exists(),(file,ref)
for css in (OUT/'assets').glob('*.css'):
    for ref in re.findall(r'url\([\'"]?([^\)\'\"]+)',css.read_text()):
        assert (css.parent/ref).exists(),(css,ref)
assert len(list(OUT.glob('product-*.html')))==6
assert not list(OUT.rglob('*.sqlite3')) and not list(OUT.rglob('config.json'))
print('Validated eight pages, all local links/assets, six sample photos, and no checkout/admin/private data.')
