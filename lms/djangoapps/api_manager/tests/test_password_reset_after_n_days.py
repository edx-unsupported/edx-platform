"""
Tests for session api with advance security features
"""
import json
import uuid
from mock import patch
from datetime import timedelta
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.translation import ugettext as _

TEST_API_KEY = str(uuid.uuid4())

@override_settings(EDX_API_KEY=TEST_API_KEY)
@patch.dict("django.conf.settings.FEATURES", {'ENFORCE_PASSWORD_POLICY': True})
@patch.dict("django.conf.settings.FEATURES", {'ADVANCED_SECURITY': True})
class UserPasswordResetTest(TestCase):
    """
    Test api_manager.session.session_list view
    """

    def setUp(self):
        """
        setup the api urls
        """
        self.session_url = '/api/sessions'
        self.user_url = '/api/users'

    @override_settings(ADVANCED_SECURITY_CONFIG={'MIN_DAYS_FOR_STUDENT_ACCOUNTS_PASSWORD_RESETS': 5})
    def test_user_must_reset_password_after_n_days(self):
        """
            Test to ensure that User session login fails
            after N days. User must reset his/her
            password after N days to login again
        """
        response = self._do_post_request(
            self.user_url, 'test2', 'Test.Me64!', email='test@edx.org',
            first_name='John', last_name='Doe', secure=True
        )
        self._assert_response(response, status=201)
        user_id = response.data['id']

        response = self._do_post_request(self.session_url, 'test2', 'Test.Me64!', secure=True)
        self.assertEqual(response.status_code, 201)

        reset_time = timezone.now() + timedelta(days=5)
        with patch.object(timezone, 'now', return_value=reset_time):
            response = self._do_post_request(self.session_url, 'test2', 'Test.Me64!', secure=True)
            message = _(
                'Your password has expired due to password policy on this account. '
                'You must reset your password before you can log in again. Please click the '
                'Forgot Password" link on this page to reset your password before logging in again.'
            )
            self._assert_response(response, status=403, message=message)

            #reset the password and then try login
            pass_reset_url = "%s/%s" % (self.user_url, str(user_id))
            response = self._do_post_pass_reset_request(
                pass_reset_url, old_password='Test.Me64!', new_password='Test!Me64@', secure=True
            )
            self.assertEqual(response.status_code,  201)

            #login successful after reset password
            response = self._do_post_request(self.session_url, 'test2', 'Test!Me64@', secure=True)
            self.assertEqual(response.status_code, 201)

    def test_password_reset_with_invalid_old_password(self):
        """
        Try (and fail) user password reset with  Invalid old_password
        """
        response = self._do_post_request(
            self.user_url, 'test2', 'Test.Me64!', email='test@edx.org',
            first_name='John', last_name='Doe', secure=True
        )
        self._assert_response(response, status=201)
        user_id = response.data['id']

        pass_reset_url = "%s/%s" % (self.user_url, str(user_id))
        response = self._do_post_pass_reset_request(
            pass_reset_url, old_password='Tes2st.Me64!',
            new_password='Test!Me64@', secure=True
        )
        self._assert_response(response, status=400)

    @override_settings(ADVANCED_SECURITY_CONFIG={'MIN_DIFFERENT_STUDENT_PASSWORDS_BEFORE_REUSE': 1,
                                                 'MIN_TIME_IN_DAYS_BETWEEN_ALLOWED_RESETS': 0})
    def test_password_reset_not_allowable_reuse(self):
        """
        Try (and fail) user password reset
        with same password as the old password
        """
        response = self._do_post_request(
            self.user_url, 'test2', 'Test.Me64!', email='test@edx.org',
            first_name='John', last_name='Doe', secure=True
        )
        self._assert_response(response, status=201)
        user_id = response.data['id']

        pass_reset_url = "%s/%s" % (self.user_url, str(user_id))
        response = self._do_post_pass_reset_request(
            pass_reset_url, old_password='Test.Me64!',
            new_password='Test.Me64!', secure=True
        )
        message = _(
            "You are re-using a password that you have used recently. You must "
            "have 1 distinct password(s) before reusing a previous password."
        )
        self._assert_response(response, status=403, message=message)

    @override_settings(ADVANCED_SECURITY_CONFIG={'MIN_DIFFERENT_STUDENT_PASSWORDS_BEFORE_REUSE': 0,
                                                 'MIN_TIME_IN_DAYS_BETWEEN_ALLOWED_RESETS': 0})
    def test_password_reset_valid_allowable_reuse(self):
        """
        Try (and pass) user password reset
        with same password as the old password
        """
        response = self._do_post_request(
            self.user_url, 'test2', 'Test.Me64!', email='test@edx.org',
            first_name='John', last_name='Doe', secure=True
        )
        self._assert_response(response, status=201)
        user_id = response.data['id']

        pass_reset_url = "%s/%s" % (self.user_url, str(user_id))
        response = self._do_post_pass_reset_request(
            pass_reset_url, old_password='Test.Me64!',
            new_password='Test.Me64!', secure=True
        )
        message = 'Password Reset Successful'
        self._assert_response(response, status=201, message=message)

    @override_settings(ADVANCED_SECURITY_CONFIG={'MIN_TIME_IN_DAYS_BETWEEN_ALLOWED_RESETS': 1})
    def test_is_password_reset_too_frequent(self):
        """
        Try reset user password before
        and after the MIN_TIME_IN_DAYS_BETWEEN_ALLOWED_RESETS
        """
        response = self._do_post_request(
            self.user_url, 'test2', 'Test.Me64!', email='test@edx.org',
            first_name='John', last_name='Doe', secure=True
        )
        self._assert_response(response, status=201)
        user_id = response.data['id']

        pass_reset_url = "%s/%s" % (self.user_url, str(user_id))
        response = self._do_post_pass_reset_request(
            pass_reset_url, old_password='Test.Me64!',
            new_password='NewP@ses34!', secure=True
        )
        message = _(
            "You are resetting passwords too frequently. Due to security policies, "
            "1 day(s) must elapse between password resets"
        )
        self._assert_response(response, status=403, message=message)

        reset_time = timezone.now() + timedelta(days=1)
        with patch.object(timezone, 'now', return_value=reset_time):
            response = self._do_post_pass_reset_request(
                pass_reset_url, old_password='Test.Me64!',
                new_password='NewP@ses34!', secure=True
            )
            message = 'Password Reset Successful'
            self._assert_response(response, status=201, message=message)

    def _do_post_request(self, url, username, password, **kwargs):
        """
        Post the login info
        """
        post_params, extra = {'username': username, 'password': password}, {}
        if kwargs.get('email'):
            post_params['email'] = kwargs.get('email')
        if kwargs.get('first_name'):
            post_params['first_name'] = kwargs.get('first_name')
        if kwargs.get('last_name'):
            post_params['last_name'] = kwargs.get('last_name')

        headers = {'X-Edx-Api-Key': TEST_API_KEY, 'Content-Type': 'application/json'}
        if kwargs.get('secure', False):
            extra['wsgi.url_scheme'] = 'https'
        return self.client.post(url, post_params, headers=headers, **extra)

    def _do_post_pass_reset_request(self, url, old_password, new_password, **kwargs):
        """
        Post the Password Reset info
        """
        post_params, extra = {'old_password': old_password, 'new_password': new_password}, {}

        headers = {'X-Edx-Api-Key': TEST_API_KEY, 'Content-Type': 'application/json'}
        if kwargs.get('secure', False):
            extra['wsgi.url_scheme'] = 'https'
        return self.client.post(url, post_params, headers=headers, **extra)

    def _assert_response(self, response, status=200, success=None, message=None):
        """
        Assert that the response had status 200 and returned a valid
        JSON-parseable dict.

        If success is provided, assert that the response had that
        value for 'success' in the JSON dict.

        If message is provided, assert that the response contained that
        value for 'message' in the JSON dict.
        """
        self.assertEqual(response.status_code, status)

        try:
            response_dict = json.loads(response.content)
        except ValueError:
            self.fail("Could not parse response content as JSON: %s"
                      % str(response.content))

        if success is not None:
            self.assertEqual(response_dict['success'], success)

        if message is not None:
            msg = ("'%s' did not contain '%s'" %
                   (response_dict['message'], message))
            self.assertTrue(message in response_dict['message'], msg)

