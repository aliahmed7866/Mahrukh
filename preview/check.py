"""Validate both demo languages, stable fixtures and the publication boundary."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
from build import OUT, build
from localize import MISSING, MESSAGES

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.refs=[];self.posts=[];self.attrs=[];self.titles=[];self.in_title=False;self.root={};self.languages={};self.controls=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.attrs.append((tag,a))
        if self.in_title:raise AssertionError('Markup inside the page title')
        if tag=='title':self.in_title=True
        if tag=='html':self.root=a
        for key in ('href','src','action'):
            if a.get(key):self.refs.append(a[key])
        if tag=='form' and a.get('method','get').lower()!='get':self.posts.append(a)
        if a.get('data-language'):self.languages[a['data-language']]=a
        if tag in ('input','option') and 'value' in a:self.controls.append((tag,a.get('name'),a['value']))
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.titles.append(data)

def check():
    build()
    assert not MISSING, sorted(MISSING)
    for source,translation in MESSAGES.items():
        assert translation.strip(), source
        assert set(re.findall(r"{(\w+)}",source))==set(re.findall(r"{(\w+)}",translation)), source
    pages={}
    for file in OUT.glob('*.html'):
        text=file.read_text();parser=Page();parser.feed(text);pages[file.name]=parser
        ur=file.name.endswith('.ur.html')
        assert parser.root=={'lang':'ur' if ur else 'en','dir':'rtl' if ur else 'ltr'}, file
        assert 'data-design-preview="true"' in text and not parser.posts
        assert 'ڈیزائن کی جھلک' in text if ur else 'DESIGN PREVIEW' in text
        assert len(parser.titles)==1 and len(parser.titles[0])<100, file
        assert not re.search(r'wa\.me|/checkout|/admin|csrf_token|seller_phone|admin_hash',text), file
        assert parser.languages.keys()=={'en','ur'}, file
        assert parser.languages['ur' if ur else 'en'].get('aria-current')=='true',file
        assert any(tag=='meta' and a.get('name')=='robots' and a.get('content')=='noindex,nofollow' for tag,a in parser.attrs), file
        for ref in parser.refs:
            parsed=urlsplit(ref)
            if parsed.scheme or not parsed.path:continue
            assert not parsed.path.startswith('/'),(file,ref)
            assert (file.parent/unquote(parsed.path)).is_file(),(file,ref)
        for tag,a in parser.attrs:
            if tag=='input':assert a.get('name') in {'q','budget','lang','demo-size'},(file,a)
    # Values without explicit option values are compared through the browser checks.
    for name,page in pages.items():
        if name.endswith('.ur.html'):continue
        other=pages[name.replace('.html','.ur.html')]
        cards=lambda parsed:[{k:v for k,v in a.items() if k in {'data-id','data-price','data-category','data-fabric','data-sizes'}} for tag,a in parsed.attrs if tag=='article' and 'data-id' in a]
        assert cards(page)==cards(other),name
    for css in (OUT/'assets').glob('*.css'):
        for ref in re.findall(r'url\([\'"]?([^\)\'\"]+)',css.read_text()):assert (css.parent/ref).is_file(),(css,ref)
    assert len(list(OUT.glob('product-*.html')))==12
    assert len(pages)==28
    allowed={'.html','.css','.js','.svg','.webp','.ttf','.txt'}
    assert all(path.name=='.nojekyll' or path.suffix in allowed for path in OUT.rglob('*') if path.is_file())
    assert (OUT/'assets/fonts/OFL.txt').is_file()
    assert len(list((OUT/'assets/photos').glob('*.webp')))==6
    print('Validated 28 pages in English/Urdu, translation coverage, stable catalog identifiers, local assets and no transactions/private data.')

if __name__=='__main__':check()
