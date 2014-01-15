from htk.test_scaffold.models import TestScaffold
from htk.test_scaffold.tests import BaseTestCase
from htk.test_scaffold.tests import BaseWebTestCase

from hacktoolkit.constants import *

class HtkWebViewsTestCase(BaseWebTestCase):

    def test_basic(self):
        self.assertTrue(True)

    def test_login_required_views(self):
        (user, client,) = self._get_user_session()

        login_required_view_names = (
        )

        for view_name in login_required_view_names:
            self._check_view_redirects_to_login(view_name)
            self._check_view_is_okay(view_name, client=client)
        
    def test_general_views(self):
        view_names = (
            'home',
            'about',
            'help',
            'tos',
            'privacy',
            # meta
            'bing_site_auth',
            'robots',
            'sitemap',
        )
        
        scaffold = TestScaffold()
        # prelaunch
        scaffold.set_fake_prelaunch(prelaunch_mode=True, prelaunch_host=False)
        for view_name in view_names:
            self._check_prelaunch_mode(view_name)

        # post-launch
        scaffold.set_fake_prelaunch(prelaunch_mode=False, prelaunch_host=False)
        for view_name in view_names:
            self._check_view_is_okay(view_name)

    def test_view_admin(self):
        view_name = 'admin:index'
        self._check_view_is_okay(view_name)

    def test_view_index(self):
        view_name = 'index'
        scaffold = TestScaffold()

        # prelaunch
        scaffold.set_fake_prelaunch(prelaunch_mode=True, prelaunch_host=False)
        self._check_prelaunch_mode(view_name)

        # post-launch
        scaffold.set_fake_prelaunch(prelaunch_mode=False, prelaunch_host=False)
        self._check_view_redirects_to_another(view_name, 'home')

####################
# Finally, import tests from subdirectories last to prevent circular import
