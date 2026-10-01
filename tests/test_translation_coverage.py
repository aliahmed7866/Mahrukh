"""Catch missing bilingual copy without pretending to verify Urdu fluency.

Run the optional raw-copy audit with::

    .venv/bin/python tests/test_translation_coverage.py --audit

The audit needs human judgment: product codes, brand names and the retained
English tagline are intentional. Normal tests validate catalog coverage and
formatting, while a fluent Urdu reviewer must approve the actual wording.
"""
import ast
from collections import defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from string import Formatter
import sys
import unittest

from jinja2 import Environment, nodes

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import CATEGORIES
from catalog import FABRICS, MEASUREMENTS, OCCASIONS, QUESTIONS
from commerce import PAYMENT_STATUSES, POLICIES, STATUSES

TEMPLATES = sorted((ROOT / 'templates').glob('*.html')) + sorted((ROOT / 'preview/templates').glob('*.html'))
PYTHON_SOURCES = ('app.py', 'boutique.py', 'commerce.py', 'i18n.py')
LIVE_SCRIPTS = ('static/i18n.js', 'static/shop.js', 'static/discovery.js', 'static/boutique.js')
JAVASCRIPT_SOURCES = (*LIVE_SCRIPTS, 'preview/preview.js')
BROWSER_CATALOGS = {'base', 'browser', 'preview'}
ENV = Environment()


def read_catalogs(browser=False):
    result = {}
    owners = {}
    for path in sorted((ROOT / 'translations').glob('*.json')):
        if browser and path.stem not in BROWSER_CATALOGS:
            continue
        messages = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(messages, dict):
            raise AssertionError(f'{path.name}: translation catalog must be an object')
        for key, value in messages.items():
            if not isinstance(key, str) or not isinstance(value, str) or not value.strip():
                raise AssertionError(f'{path.name}: invalid or empty translation for {key!r}')
            if key in result and result[key] != value:
                raise AssertionError(f'Conflicting translation for {key!r}: {owners[key]}, {path.name}')
            result[key] = value
            owners[key] = path.name
    return result


def jinja_literal_strings(expression):
    if isinstance(expression, nodes.Const) and isinstance(expression.value, str):
        yield expression.value
    elif isinstance(expression, nodes.CondExpr):
        yield from jinja_literal_strings(expression.expr1)
        if expression.expr2 is not None:
            yield from jinja_literal_strings(expression.expr2)


def template_messages():
    result = defaultdict(set)
    for path in TEMPLATES:
        tree = ENV.parse(path.read_text(encoding='utf-8'))
        for call in tree.find_all(nodes.Call):
            if isinstance(call.node, nodes.Name) and call.node.name == 't' and call.args:
                for message in jinja_literal_strings(call.args[0]):
                    result[message].add(f'{path.relative_to(ROOT)}:{call.lineno}')
    return result


def python_messages():
    result = defaultdict(set)
    for name in PYTHON_SOURCES:
        tree = ast.parse((ROOT / name).read_text(encoding='utf-8'), filename=name)
        for call in ast.walk(tree):
            if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                    and call.func.id == 't' and call.args):
                continue
            argument = call.args[0]
            choices = (argument.body, argument.orelse) if isinstance(argument, ast.IfExp) else (argument,)
            for choice in choices:
                if isinstance(choice, ast.Constant) and isinstance(choice.value, str):
                    result[choice.value].add(f'{name}:{call.lineno}')
    return result


# This intentionally checks simple quoted literals only. Runtime data and
# ternaries are covered by the explicit dynamic-message sets below.
JS_T_LITERAL = re.compile(r'''(?<![\w$.])t\(\s*("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')''')


def javascript_messages(paths=JAVASCRIPT_SOURCES):
    result = defaultdict(set)
    for name in paths:
        source = (ROOT / name).read_text(encoding='utf-8')
        for match in JS_T_LITERAL.finditer(source):
            message = ast.literal_eval(match.group(1))
            line = source.count('\n', 0, match.start()) + 1
            result[message].add(f'{name}:{line}')
    return result


def format_fields(message):
    return {field for _, field, _, _ in Formatter().parse(message) if field is not None}


class TranslationCoverageTests(unittest.TestCase):
    def assert_covered(self, messages, catalog):
        missing = [f'{message!r}: {", ".join(sorted(locations))}'
                   for message, locations in sorted(messages.items()) if message not in catalog]
        self.assertFalse(missing, 'Missing Urdu messages:\n' + '\n'.join(missing))

    def test_jinja_literal_messages_are_covered(self):
        self.assert_covered(template_messages(), read_catalogs())

    def test_python_literal_messages_are_covered(self):
        self.assert_covered(python_messages(), read_catalogs())

    def test_javascript_messages_are_covered_and_live_messages_are_exported(self):
        self.assert_covered(javascript_messages(), read_catalogs())
        self.assert_covered(javascript_messages(LIVE_SCRIPTS), read_catalogs(browser=True))

    def test_dynamic_customer_labels_are_covered(self):
        labels = set(CATEGORIES) | set(FABRICS) | set(OCCASIONS.values()) | set(MEASUREMENTS.values())
        labels |= set(POLICIES.values()) | {label.title() for label in (*STATUSES, *PAYMENT_STATUSES)}
        labels |= {value for pair in QUESTIONS.values() for value in pair}
        labels |= {'Cash on delivery', 'Manual transfer', 'sample piece', 'sample pieces',
                   'Search results', 'The sample collection',
                   'Included', 'Not included', 'Composition', 'Lining & opacity', 'Fit',
                   'Care', 'Fabric dimensions', 'Craft & origin', 'Product dispatch note'}
        self.assert_covered({label: {'dynamic customer label'} for label in labels}, read_catalogs())

    def test_format_placeholders_match_and_translations_have_urdu_text(self):
        # Platform names are proper nouns, deliberately retained in Latin script.
        proper_names = {'Instagram', 'Facebook', 'TikTok', 'YouTube', 'WhatsApp', 'Safepay', 'PayPal'}
        for source, translated in read_catalogs().items():
            with self.subTest(message=source):
                self.assertEqual(format_fields(source), format_fields(translated))
                if source not in proper_names:
                    self.assertRegex(translated, r'[\u0600-\u06ff]', 'Translation needs Urdu copy or an explicit proper-name exception')


class RawCopyAudit(HTMLParser):
    """Report potential untranslated copy; do not make it a brittle test gate."""
    def __init__(self):
        super().__init__()
        self.skipped = 0
        self.candidates = set()

    def consider(self, text):
        clean = ' '.join(text.replace('__dynamic__', '').split())
        if re.search(r'[A-Za-z]{2,}', clean):
            self.candidates.add(clean)

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skipped += 1
        for key, value in attrs:
            if value and key in ('alt', 'title', 'placeholder', 'aria-label', 'aria-description'):
                self.consider(value)

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skipped = max(0, self.skipped - 1)

    def handle_data(self, data):
        if not self.skipped:
            self.consider(data)


def audit_raw_copy():
    seller_templates = {'admin.html', 'admin_order.html', 'edit.html', 'edit_facts.html', 'insights.html',
                        'login.html', 'settings.html', 'orders.html', 'icons.html'}
    for path in TEMPLATES:
        if path.parent.name == 'templates' and path.parent.parent == ROOT and path.name in seller_templates:
            continue
        fragments = []
        for _, token, value in ENV.lex(path.read_text(encoding='utf-8')):
            if token == 'data':
                fragments.append(value)
            elif token == 'variable_begin':
                fragments.append('__dynamic__')
        audit = RawCopyAudit()
        audit.feed(''.join(fragments))
        if audit.candidates:
            print(path.relative_to(ROOT))
            for candidate in sorted(audit.candidates):
                print('  ' + candidate)


if __name__ == '__main__':
    if '--audit' in sys.argv:
        audit_raw_copy()
    else:
        unittest.main()
