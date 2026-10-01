"""Validate both static locales, local links and the no-transactions boundary."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
if __package__:
    from .build import OUT, build
else:
    from build import OUT, build


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.posts, self.language_links, self.inputs = [], [], [], []
        self.html = {}
        self.preview = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'html':
            self.html = attributes
        if tag == 'body':
            self.preview = attributes.get('data-design-preview') == 'true'
        for key in ('href', 'src', 'action'):
            if attributes.get(key):
                self.refs.append(attributes[key])
        if tag == 'form' and attributes.get('method', 'get').lower() != 'get':
            self.posts.append(attributes)
        if 'data-language-link' in attributes:
            self.language_links.append(attributes)
        if tag == 'input':
            self.inputs.append(attributes)


def validate():
    for locale in ('en', 'ur'):
        folder = OUT / 'ur' if locale == 'ur' else OUT
        pages = list(folder.glob('*.html'))
        assert len(pages) == 13, (locale, len(pages))
        assert len(list(folder.glob('product-*.html'))) == 6
        for file in pages:
            source = file.read_text()
            parser = Links()
            parser.feed(source)
            assert parser.html.get('lang') == locale, file
            assert parser.html.get('dir') == ('rtl' if locale == 'ur' else 'ltr'), file
            assert parser.preview and not parser.posts, file
            assert not re.search(r'wa\.me|/checkout|/admin|csrf_token|seller_phone|admin_hash', source), file
            assert not any(field.get('name') in {'customer_name', 'phone', 'address', 'email'} for field in parser.inputs), file
            assert len(parser.language_links) == 2, file
            assert [link['data-language'] for link in parser.language_links if link.get('aria-current') == 'true'] == [locale], file
            for link in parser.language_links:
                target = (file.parent / unquote(urlsplit(link['href']).path)).resolve()
                expected = OUT / ('ur/' if link['data-language'] == 'ur' else '') / file.name
                assert target == expected.resolve(), (file, link)
            notice = 'ڈیزائن کا پیش منظر' if locale == 'ur' else 'DESIGN PREVIEW'
            assert notice in source, file
            for ref in parser.refs:
                parsed = urlsplit(ref)
                if parsed.scheme or not parsed.path:
                    continue
                assert not parsed.path.startswith('/'), (file, ref)
                target = (file.parent / unquote(parsed.path)).resolve()
                assert target.is_relative_to(OUT.resolve()), (file, ref)
                assert target.exists(), (file, ref)
    for css in (OUT / 'assets').glob('*.css'):
        for ref in re.findall(r'url\([\'"]?([^\)\'\"]+)', css.read_text()):
            if ref.startswith('data:'):
                continue
            assert (css.parent / ref).exists(), (css, ref)
    assert (OUT / 'assets/fonts/NotoNaskhArabic-Variable.ttf').is_file()
    assert not list(OUT.rglob('*.sqlite3')) and not list(OUT.rglob('config.json'))
    assert len(list(OUT.rglob('*.html'))) == 26
    print('Validated 26 English/Urdu pages, language links, local fonts/assets, and no transactions/private data.')


if __name__ == '__main__':
    build()
    validate()
