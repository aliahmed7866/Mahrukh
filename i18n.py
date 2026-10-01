"""Small, local English/Urdu translation layer shared by Flask and the preview.

English source messages are stable catalog keys. Seller facts are never translated
automatically. UI translations are draft copy pending a fluent Urdu review.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode
import json

from flask import g, has_request_context, request
from markupsafe import Markup, escape

LANGUAGES = ('en', 'ur')
COOKIE = 'mahrukh_language'
_preview_locale = ContextVar('mahrukh_preview_locale', default=None)


@lru_cache(maxsize=2)
def _catalog(browser=False):
    result = {}
    for path in sorted((Path(__file__).parent / 'translations').glob('*.json')):
        if browser and path.stem not in ('browser', 'preview', 'base'):
            continue
        messages = json.loads(path.read_text(encoding='utf-8'))
        for key, value in messages.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(f'Invalid translation in {path.name}')
            if key in result and result[key] != value:
                raise ValueError(f'Conflicting translation for {key!r} in {path.name}')
            result[key] = value
    return result


def current_locale():
    override = _preview_locale.get()
    if override:
        return override
    if has_request_context():
        # The seller studio is intentionally English for this release.
        if request.path.startswith('/admin'):
            return 'en'
        chosen = request.args.get('lang')
        if chosen in LANGUAGES:
            return chosen
        remembered = request.cookies.get(COOKIE)
        return remembered if remembered in LANGUAGES else 'en'
    return 'en'


@contextmanager
def use_locale(locale):
    """Render a static preview without a Flask application/request."""
    token = _preview_locale.set(locale if locale in LANGUAGES else 'en')
    try:
        yield
    finally:
        _preview_locale.reset(token)


def translation_catalog(locale=None, browser=False):
    messages = _catalog(browser)
    return dict(messages) if (locale or current_locale()) == 'ur' else {key: key for key in messages}


def t(message, **values):
    source = str(message)
    text = _catalog().get(source, source) if current_locale() == 'ur' else source
    return text.format(**values) if values else text


def localized(obj, key):
    """Get an optional seller translation without mutating canonical records."""
    if current_locale() == 'ur':
        translated = obj.get(key + '_ur') or (obj.get('translations') or {}).get(key)
        if translated:
            return str(translated)
    return str(obj.get(key) or '')


def content(obj, key):
    """Escape seller prose and clearly mark a missing Urdu translation."""
    original = str(obj.get(key) or '')
    translated = obj.get(key + '_ur') or (obj.get('translations') or {}).get(key)
    if current_locale() == 'ur' and translated:
        return Markup('<span lang="ur" dir="rtl">{}</span>').format(escape(translated))
    if current_locale() == 'ur' and original:
        return Markup('<span class="english-fallback"><span class="fallback-label" lang="en" dir="ltr">English</span> <span lang="en" dir="ltr">{}</span></span>').format(escape(original))
    # Preserve the existing English DOM where no language override is necessary.
    return escape(original)


def language_url(locale):
    """Equivalent GET page, keeping filters and stable identifiers only in place."""
    args = [(key, value) for key, values in request.args.lists() if key != 'lang' for value in values]
    args.append(('lang', locale if locale in LANGUAGES else 'en'))
    return request.path + '?' + urlencode(args)


def install_i18n(app):
    @app.before_request
    def select_language():
        g.locale = current_locale()

    @app.after_request
    def language_headers(response):
        response.headers['Content-Language'] = current_locale()
        chosen = request.args.get('lang')
        if chosen in LANGUAGES and request.endpoint not in ('static', 'media', 'health'):
            response.set_cookie(COOKIE, chosen, max_age=365 * 24 * 3600,
                                secure=app.config.get('SESSION_COOKIE_SECURE', False),
                                httponly=True, samesite='Lax')
        return response

    @app.url_defaults
    def retain_explicit_language(endpoint, values):
        # Urdu navigation works with cookies disabled as well as with JS disabled.
        if current_locale() == 'ur' and endpoint not in ('static', 'media', 'health') and not endpoint.startswith('admin') and endpoint not in ('login', 'shop_settings', 'insights'):
            values.setdefault('lang', 'ur')

    @app.context_processor
    def language_context():
        locale = current_locale()
        return dict(t=t, localized=localized, content=content, locale=locale,
                    direction='rtl' if locale == 'ur' else 'ltr',
                    language_url=language_url, translation_catalog=translation_catalog)
