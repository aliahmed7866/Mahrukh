"""Build-time translation of the allowlisted static demo, never live inventory.

Exact, normalized English messages are keys in ur.json. The checker rejects
untranslated visible copy so shared template changes cannot silently ship gaps.
Identifiers, form values and data used for price/size calculations stay stable.
"""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from urllib.parse import urlsplit, urlunsplit

HERE = Path(__file__).parent
MESSAGES = json.loads((HERE / 'ur.json').read_text()) if (HERE / 'ur.json').exists() else {}
KEEP = {'English', 'اردو', 'MAHRUKH', 'Mahrukh', 'Instagram', 'Facebook', 'TikTok', 'S', 'M', 'L', 'XL', 'XS', '2XL', '3XL', 'PKR'}
MISSING = set()

def normal(text):
    return ' '.join(text.split())

def translate(text):
    key = normal(text)
    if not key or key in KEEP or not re.search('[A-Za-z]', key):
        return text
    if key in MESSAGES:
        return re.match(r'^\s*', text)[0] + MESSAGES[key] + re.search(r'\s*$', text)[0]
    if re.fullmatch(r'PKR [\d,.]+', key):
        return text
    MISSING.add(key)
    return text

def localized_url(value):
    url = urlsplit(value)
    if not url.scheme and not url.netloc and url.path.endswith('.html') and not url.path.endswith('.ur.html'):
        return urlunsplit(url._replace(path=url.path[:-5]+'.ur.html'))
    return value

class Localizer(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output=[]
        self.stack=[]
    def handle_decl(self, decl): self.output.append('<!'+decl+'>')
    def handle_comment(self, data): self.output.append('<!--'+data+'-->')
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        skip=(self.stack[-1][1] if self.stack else False) or tag in {'script','style'} or a.get('lang') in {'en','ur'} or a.get('dir')=='ltr'
        # The original root's language must not inhibit translation of descendants.
        if tag=='html': a.update(lang='ur',dir='rtl');skip=False
        if tag=='option' and 'value' not in a:
            # These options have a single text node; set their value in handle_data.
            a['data-original-option']='true'
        for key in ('alt','aria-label','placeholder','title','data-question','data-product-name','data-piece-name'):
            if a.get(key):a[key]=translate(a[key])
        if tag=='meta' and a.get('name')=='description':a['content']=translate(a['content'])
        if a.get('data-language'):
            a.pop('aria-current',None)
            if a['data-language']=='ur':a['aria-current']='true'
        else:
            for key in ('href','action'):
                if a.get(key):a[key]=localized_url(a[key])
        if tag=='option' and a.pop('data-original-option',None):
            self.pending_option=(len(self.output),a)
        self.output.append('<'+tag+''.join(' '+k+('="'+escape(v,quote=True)+'"' if v is not None else '') for k,v in a.items())+'>')
        if tag not in self.VOID:self.stack.append((tag,skip))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        self.output.append('</'+tag+'>')
        if self.stack and self.stack[-1][0]==tag:self.stack.pop()
    def handle_data(self,data):
        if self.stack and self.stack[-1][0]=='option' and hasattr(self,'pending_option'):
            pos,a=self.pending_option;a['value']=data
            self.output[pos]='<option'+''.join(' '+k+('="'+escape(v,quote=True)+'"' if v is not None else '') for k,v in a.items())+'>'
            del self.pending_option
        raw=self.stack and self.stack[-1][0] in {'script','style'}
        skip=self.stack and self.stack[-1][1]
        if not skip and re.fullmatch(r'(?:PKR [\d,.]+|XS|S|M|L|XL|2XL|3XL)', data.strip()):
            self.output.append('<bdi dir="ltr" lang="en">'+escape(data)+'</bdi>')
        else:
            self.output.append(data if raw else escape(data if skip else translate(data)))

def localize(html):
    parser=Localizer();parser.feed(html);return ''.join(parser.output)
