from django.test.client import Client

from htk.test_scaffold.helpers import create_test_email
from htk.test_scaffold.helpers import create_test_password
from htk.test_scaffold.helpers import create_test_user_with_email_and_password
from htk.test_scaffold.tests import BaseTestCase
from htk.test_scaffold.tests import BaseWebTestCase

from accounts.utils import associate_user_email
from accounts.utils import get_user_by_email
from accounts.utils import get_user_email

class AccountTestCase(BaseTestCase):
    def setUp(self):
        super(AccountTestCase, self).setUp()

    def test_user_profile(self):
        user = self._assign_test_user()
        profile = user.profile
        self.assertIsNotNone(profile)

class AccountViewsTestCase(BaseWebTestCase):
    def setUp(self):
        super(AccountViewsTestCase, self).setUp()

    def test_basic(self):
        self.assertTrue(True)

    def test_login_required_views(self):
        (user, client,) = self._get_user_session()

        login_required_view_names = (
            'account_settings',
        )

        for view_name in login_required_view_names:
            self._check_view_redirects_to_login(view_name)
            self._check_view_is_okay(view_name, client=client)

    def test_login_not_required_views(self):
        login_not_required_view_names = (
            'account_login',
            'account_register',
            'account_register_done',
            'account_resend_confirmation',
            # password reset
            'account_forgot_password',
            'account_password_reset_done',
            'account_reset_password',
            'account_password_reset_success',            
        )

        for view_name in login_not_required_view_names:
            self._check_view_is_okay(view_name)


    def test_view_index(self):
        view_name = 'account_index'

        self._check_view_redirects_to_login(view_name)
        (user, client,) = self._get_user_session()
        self._check_view_redirects_to_another(view_name, 'account_home', client=client)

    def test_view_home(self):
        view_name = 'account_home'

        self._check_view_redirects_to_login(view_name)
        (user, client,) = self._get_user_session()
        self._check_view_redirects_to_another(view_name, 'account_settings', client=client)

    def test_view_register(self):
        view_name = 'account_register'

        email = create_test_email()
        password = create_test_password()

        user = get_user_by_email(email)
        self.assertIsNone(user,
                          'The user with email [%s] should not exist before registration.' %
                          email)

        params = {
            'email' : email,
            'password1' : password,
            'password2' : password,
        }
        response = self._post(view_name, params=params, follow=True)
        redirect_chain = response.redirect_chain
        self.assertTrue(len(redirect_chain) > 0,
                        'Registration should have succeeded')

        user = get_user_by_email(email)
        self.assertIsNotNone(user,
                             'The user with email [%s] should exist after registration.' %
                             email)

        self.assertFalse(user.is_active,
                         'User should not be active until email address is confirmed')
        self.assertEqual(email,
                         user.email,
                         'User email does not match registration email')

        # should not be able to register twice
        response = self._post(view_name, params=params, follow=True)
        redirect_chain = response.redirect_chain
        self.assertTrue(len(redirect_chain) == 0,
                        'Repeat registration should have failed.')
        self.assertEqual(200,
                         response.status_code,
                         'Repeat registration should have failed.')

        
        client = Client()
        login_success = client.login(username=user.username, password=password)
        self.assertFalse(login_success,
                        'Should not be able to log in before account is activated, after registration')

        user_email = get_user_email(user, email)
        user_email.confirm_and_activate_account()

        client = Client()
        login_success = client.login(username=user.username, password=password)
        self.assertTrue(login_success,
                        'Should be able to log in after account is activated, after registration')

        # register post when already logged in
        # this can happen if someone is logged out, goes to register page
        # and then logs in in a separate tab, leaving register page open
        self._check_view_redirects_to_another(view_name,
                                              'account_home',
                                              client=client,
                                              params=params)

    def test_view_login_post(self):
        view_name = 'account_login'

        (user, email, password,) = create_test_user_with_email_and_password()
        user_email = associate_user_email(user, email)

        # login with unconfirmed email
        params = {
            'email' : email,
            'password' : password,
        }
        response = self._post(view_name, params=params, follow=True)
        redirect_chain = response.redirect_chain
        self.assertEqual(200,
                         response.status_code,
                         'Should not be able to log in with an unconfirmed email.')
        self.assertEqual(0,
                         len(redirect_chain),
                         'Should not be able to log in with an unconfirmed email.')

        # login with confirmed email
        user_email.is_confirmed = True
        user_email.save()
#        self._check_view_redirects_to_another(view_name,
#                                              'account_home',
#                                              params=params,
#                                              method='post')

        # login with incorrect password
        params['password'] = 'wrong_password'
        response = self._post(view_name, params=params, follow=True)
        redirect_chain = response.redirect_chain
        self.assertEqual(200,
                         response.status_code,
                         'Should not be able to log in with an incorrect password.')
        self.assertEqual(0,
                         len(redirect_chain),
                         'Should not be able to log in with an incorrect password.')

        # login post when already logged in
        # this can happen if someone is logged out, goes to login page
        # and then logs in in a separate tab, leaving login page open
        client = Client()
        client.login(username=user.username, password=password)
        self._check_view_redirects_to_another(view_name,
                                              'account_home',
                                              client=client,
                                              params=params)

    def test_view_logout(self):
        view_name = 'account_logout'
        # logged out
        response = self._get(view_name)
        self.assertEqual(302, response.status_code)
        # logged in
        (user, client,) = self._get_user_session()
        response = self._get(view_name, client=client)
        self.assertEqual(302, response.status_code)

    def test_view_confirm_email(self):
        view_name = 'account_confirm_email'
        # invalid confirmation code
        args = ('asdf1234',)
        response = self._get(view_name, view_args = args)
        self.assertEqual(404,
                         response.status_code,
                         'Should not be able to confirm with invalid code')

        # valid confirmation code
        (user, email, password,) = create_test_user_with_email_and_password()
        user_email = associate_user_email(user, email)
        args = (user_email.activation_key,)
        response = self._get(view_name, view_args = args)
        self.assertEqual(200,
                         response.status_code,
                         'Should able to confirm with valid code')
