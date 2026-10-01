"""Export-specific language and non-selling boundary regressions."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from jinja2 import Environment, nodes
from preview import build as exporter
from preview import check
from i18n import translation_catalog


class PreviewLanguages(unittest.TestCase):
    def test_bilingual_export_boundaries_and_stable_product_values(self):
        with tempfile.TemporaryDirectory(dir=exporter.ROOT) as temporary:
            destination = Path(temporary) / 'site'
            with patch.object(exporter, 'OUT', destination), patch.object(check, 'OUT', destination):
                exporter.build()
                check.validate()
                products = json.loads((exporter.HERE / 'products.json').read_text())
                for product in products:
                    for locale in ('en', 'ur'):
                        folder = destination / 'ur' if locale == 'ur' else destination
                        page = (folder / f"product-{product['id']}.html").read_text()
                        self.assertIn(f'data-id="{product["id"]}"', page)
                        self.assertIn(f'data-price="{product["price"]}"', page)
                        for size in product['sizes']:
                            self.assertIn(f'name="demo-size" value="{size}"', page)
                for locale in ('en', 'ur'):
                    folder = destination / 'ur' if locale == 'ur' else destination
                    parser = check.Links()
                    parser.feed((folder / 'index.html').read_text())
                    # Both stored language texts are searchable in either UI locale.
                    index = (folder / 'index.html').read_text()
                    for product in products:
                        self.assertIn(product['name'], index)
                        self.assertIn(product['name_ur'], index)

    def test_preview_template_messages_have_urdu_entries(self):
        catalog = translation_catalog('ur')
        for path in (exporter.HERE / 'templates').glob('*.html'):
            ast = Environment().parse(path.read_text())
            for call in ast.find_all(nodes.Call):
                if getattr(call.node, 'name', '') == 't' and call.args and isinstance(call.args[0], nodes.Const):
                    with self.subTest(template=path.name, message=call.args[0].value):
                        self.assertIn(call.args[0].value, catalog)


if __name__ == '__main__':
    unittest.main()
