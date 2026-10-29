import unittest

from resource_coverage_contract import validate_coverage


class ResourceCoverageContractTests(unittest.TestCase):
    def test_exact_coverage_passes(self):
        validate_coverage({'index.html': [], 'history/emma-hale-smith.html': []},
                          {'index.html', 'history/emma-hale-smith.html'})

    def test_missing_current_page_fails(self):
        with self.assertRaises(AssertionError):
            validate_coverage({'index.html': []}, {'index.html', 'history/emma-hale-smith.html'})

    def test_unexpected_extra_page_fails(self):
        with self.assertRaises(AssertionError):
            validate_coverage({'index.html': [], 'unexpected.html': []}, {'index.html'})

    def test_retired_page_fails(self):
        with self.assertRaises(AssertionError):
            validate_coverage({'index.html': [], 'history/emma-elect-lady.html': []}, {'index.html'})


if __name__ == '__main__':
    unittest.main()
