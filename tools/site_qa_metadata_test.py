"""Semantic metadata regression: order is irrelevant; missing data still fails."""
import unittest

from site_qa import RefParser, shared_controller_count


class MetadataTest(unittest.TestCase):
    def parse(self, text):
        parser = RefParser()
        parser.feed(text)
        return parser

    def test_both_attribute_orders(self):
        for text in (
            '<link rel="canonical" href="https://focuschrist.com/example.html"><meta name="description" content="Study Christ.">',
            '<link href="https://focuschrist.com/example.html" rel="canonical"/><meta content="Study Christ." name="description"/>',
        ):
            with self.subTest(text=text):
                parser = self.parse(text)
                self.assertEqual(parser.canonicals, ['https://focuschrist.com/example.html'])
                self.assertEqual(parser.descriptions, ['Study Christ.'])

    def test_missing_wrong_and_duplicate_canonical(self):
        for text in ('', '<link rel="canonical">', '<link href="https://focuschrist.com/example.html">', '<link rel="canonical" href="https://wrong.example/">', '<link rel="canonical" href="https://focuschrist.com/example.html">' * 2):
            with self.subTest(text=text):
                self.assertNotEqual(self.parse(text).canonicals, ['https://focuschrist.com/example.html'])

    def test_missing_empty_and_duplicate_description(self):
        for text in ('', '<meta name="description">', '<meta content="Text">', '<meta name="description" content=" ">', '<meta name="description" content="Text">' * 2):
            with self.subTest(text=text):
                values = self.parse(text).descriptions
                self.assertFalse(len(values) == 1 and bool(values[0].strip()))

    def test_comments_do_not_supply_metadata(self):
        parser = self.parse('<!-- <link rel="canonical" href="https://focuschrist.com/example.html"><meta name="description" content="Text"> -->')
        self.assertEqual(parser.canonicals, [])
        self.assertEqual(parser.descriptions, [])

    def test_controller_order_and_missing_fields(self):
        for text in ('<script src="../site-common.js?v=1" defer></script>', '<script defer="" src="../site-common.js?v=1"></script>'):
            self.assertEqual(shared_controller_count(self.parse(text), '../'), 1)
        for text in ('', '<script src="../site-common.js"></script>', '<script defer></script>', '<script src="../other.js" defer></script>', '<script src="../site-common.js" defer></script>' * 2):
            self.assertNotEqual(shared_controller_count(self.parse(text), '../'), 1)


if __name__ == '__main__':
    unittest.main()
