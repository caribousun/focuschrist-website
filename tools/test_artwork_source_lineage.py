"""A shared code container must never imply shared artwork identity."""
import ast
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit

SOURCE = Path(__file__).with_name('audit_artwork_occurrences.py')
tree = ast.parse(SOURCE.read_text())
function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'source_lineage_token')
namespace = {'Path': Path, 're': re, 'urlsplit': urlsplit}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), 'exec'), namespace)
token = namespace['source_lineage_token']

class SourceLineageTests(unittest.TestCase):
    def test_shared_stylesheet_does_not_merge_distinct_mission_scenes(self):
        for asset in ('early-missionaries-liverpool-1400.webp', 'light-across-world.webp', 'service-missionaries-food-pantry-1400.webp', 'sister-missionaries-teaching-1400.webp'):
            row = {'asset': 'assets/missionary/' + asset, 'source_file': 'site-system.css', 'kind': 'stylesheet-literal'}
            self.assertIsNone(token(row, 'source_file'))

    def test_nonimage_containers_rejected_without_kind(self):
        for value in ('site-system.css', 'artwork.js', 'inventory.json', 'page.html', 'source.txt'):
            for field in ('source_file', 'source_path', 'source_original'):
                self.assertIsNone(token({field: value}, field))

    def test_code_inventory_cannot_smuggle_image_or_hash(self):
        for kind in ('stylesheet-literal', 'script-literal'):
            for field,value in [('source_file','assets/reference.png'), ('source_sha256','a'*64)]:
                self.assertIsNone(token({'kind':kind,field:value},field))

    def test_image_sources_and_valid_hashes_remain_candidates(self):
        self.assertEqual(token({'source_file':'C:\\art\\original.PNG'},'source_file'),('source_file','C:/art/original.PNG'))
        self.assertEqual(token({'source_path':'https://example.org/original.webp?x=1'},'source_path'),('source_path','https://example.org/original.webp?x=1'))
        for field in ('source_sha256','source_decoded_rgb_sha256'):
            self.assertEqual(token({field:'a'*64},field),(field,'a'*64))
            self.assertIsNone(token({field:'site-system.css'},field))

if __name__ == '__main__':
    unittest.main()
