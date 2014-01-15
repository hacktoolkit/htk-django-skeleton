from django.utils import unittest

import scripts.update_static_asset_version

class ScriptsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_updates_static_version(self):
        """Test that it runs
        """
        scripts.update_static_asset_version.main()
