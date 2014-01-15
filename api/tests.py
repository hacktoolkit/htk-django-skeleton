import json

from htk.test_scaffold.tests import BaseTestCase
from htk.test_scaffold.tests import BaseWebTestCase

from api.constants import *

class ApiTestCase(BaseWebTestCase):

    def test_basic(self):
        self.assertTrue(True)

####################
# Finally, import tests from subdirectories last to prevent circular import
#from api.accounts.tests import *
#from api.users.tests import *
