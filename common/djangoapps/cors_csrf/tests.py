from mock import patch, Mock

from django.test import TestCase
from django.test.utils import override_settings
from django.middleware.csrf import CsrfViewMiddleware

from cors_csrf.middleware import CorsCSRFMiddleware


class Sentinel():
    pass


SENTINEL = Sentinel()


class TestCorsMiddlewareProcessRequest(TestCase):
    def get_request(self, is_secure, HTTP_REFERER):
        request = Mock()
        request.META = {'HTTP_REFERER': HTTP_REFERER}
        request.is_secure = lambda: is_secure
        return request

    def setUp(self):
        self.middleware = CorsCSRFMiddleware()

    def check_not_enabled(self, request):
        with patch.object(CsrfViewMiddleware, 'process_view') as mock_method:
            res = self.middleware.process_view(request, None, None, None)

        self.assertIsNone(res)
        self.assertFalse(mock_method.called)

    def check_enabled(self, request):
        def check_req_is_secure_false(request, callback, callback_args, callback_kwargs):
            self.assertFalse(request.is_secure())
            return SENTINEL

        with patch.object(CsrfViewMiddleware, 'process_view') as mock_method:
            mock_method.side_effect = check_req_is_secure_false
            res = self.middleware.process_view(request, None, None, None)

        self.assertIs(res, SENTINEL)
        self.assertTrue(request.is_secure())

    def test_middleware(self):
        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=True,
                                       HTTP_REFERER='https://foo.com/bar')
            self.check_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': False},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=True,
                                       HTTP_REFERER='https://foo.com/bar')
            self.check_not_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['bar.com']):
            request = self.get_request(is_secure=True,
                                       HTTP_REFERER='https://foo.com/bar')
            self.check_not_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=False,
                                       HTTP_REFERER='https://foo.com/bar')
            self.check_not_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=True,
                                       HTTP_REFERER='https://bar.com/bar')
            self.check_not_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=True,
                                       HTTP_REFERER='http://foo.com/bar')
            self.check_not_enabled(request)
