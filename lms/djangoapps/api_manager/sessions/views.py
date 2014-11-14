# pylint: disable=E1101

""" API implementation for session-oriented interactions. """
from datetime import datetime
import logging

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from api_manager.permissions import SecureAPIView
from rest_framework import status
from rest_framework.response import Response


from util.bad_request_rate_limiter import BadRequestRateLimiter
from api_manager.utils import generate_base_uri

from api_manager.users.serializers import UserSerializer
from student.models import (
    LoginFailures, PasswordHistory
)
AUDIT_LOG = logging.getLogger("audit")

def _get_all_logged_in_users():
    # Query all non-expired sessions
    sessions = Session.objects.filter(expire_date__gte=datetime.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)


def _get_user_session(user):
    user_session = None
    sessions = Session.objects.filter(expire_date__gte=datetime.now())
    for session in sessions:
        data = session.get_decoded()
        if user.id == data.get('_auth_user_id', None):
            user_session = session
            user_session_store = _get_session_store(session.session_key)
            user_session.get_expiry_age = user_session_store.get_expiry_age
    return user_session


def _is_logged_in(user):
    try:
        logged_in_user = _get_all_logged_in_users().get(id=user.id)
        logged_in = True
    except User.DoesNotExist:
        logged_in = False
    return logged_in

def _get_session_store(session_id):
    engine = import_module(settings.SESSION_ENGINE)
    session_store = engine.SessionStore(session_id)
    return session_store


class SessionsList(SecureAPIView):
    """
    **Use Case**

        SessionsList creates a new session with the edX LMS.

    **Example Request**

        POST  {"username": "staff", "password": "edx"}

    **Response Values**

        * token: A unique token value for the session created.
        * expires: The number of seconds until the new session expires.
        * user: The following data about the user for whom the session is
          created.
            * id: The unique user identifier.
            * email: The user's email address.
            * username: The user's edX username.
            * first_name: The user's first name, if defined.
            * last_name: The user's last name, if defined.
            * creaed:  The time and date the user account was created.
            * organizations: An array of organizations the user is associated
              with.
        * uri: The URI to use to get details about the new session.
    """

    def post(self, request):
        response_data = {}
        # Add some rate limiting here by re-using the RateLimitMixin as a helper class
        limiter = BadRequestRateLimiter()
        if limiter.is_rate_limit_exceeded(request):
            response_data['message'] = _('Rate limit exceeded in api login.')
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)

        base_uri = generate_base_uri(request)
        try:
            existing_user = User.objects.get(username=request.DATA['username'])
        except ObjectDoesNotExist:
            existing_user = None


        if existing_user:

            # see if account has been locked out due to excessive login failures
            if LoginFailures.is_feature_enabled():
                if LoginFailures.is_user_locked_out(existing_user):
                    response_status = status.HTTP_403_FORBIDDEN
                    response_data['message'] = _('This account has been temporarily locked due to excessive login failures. '
                                                 'Try again later.')
                    return Response(response_data, status=response_status)

             # see if the user must reset his/her password due to any policy settings
            if PasswordHistory.should_user_reset_password_now(existing_user):
                response_status = status.HTTP_403_FORBIDDEN
                response_data['message'] = _(
                    'Your password has expired due to password policy on this account. '
                    'You must reset your password before you can log in again.'
                )
                return Response(response_data, status=response_status)

            user = authenticate(username=existing_user.username, password=request.DATA['password'])
            if user is not None:

                # successful login, clear failed login attempts counters, if applicable
                if LoginFailures.is_feature_enabled():
                    LoginFailures.clear_lockout_counter(user)
                if user.is_active:
                    if _is_logged_in(user):
                        user_session = _get_user_session(user)
                        response_data['token'] = user_session.session_key
                        response_data['expires'] = user_session.get_expiry_age()
                        user_dto = UserSerializer(user)
                        response_data['user'] = user_dto.data
                        response_data['uri'] = '{}/{}'.format(base_uri, user_session.session_key)
                        response_status = status.HTTP_200_OK
                    else:
                        login(request, user)
                        response_data['token'] = request.session.session_key
                        response_data['expires'] = request.session.get_expiry_age()
                        user_dto = UserSerializer(user)
                        response_data['user'] = user_dto.data
                        response_data['uri'] = '{}/{}'.format(base_uri, request.session.session_key)
                        response_status = status.HTTP_201_CREATED
                    # add to audit log
                    AUDIT_LOG.info(u"API::User logged in successfully with user-id - {0}".format(user.id))
                else:
                    response_status = status.HTTP_403_FORBIDDEN
            else:
                limiter.tick_bad_request_counter(request)
                # tick the failed login counters if the user exists in the database
                if LoginFailures.is_feature_enabled():
                    LoginFailures.increment_lockout_counter(existing_user)

                response_status = status.HTTP_401_UNAUTHORIZED
                AUDIT_LOG.warn(u"API::User authentication failed with user-id - {0}".format(existing_user.id))
        else:
            AUDIT_LOG.warn(u"API::Failed login attempt with unknown email/username")
            response_status = status.HTTP_404_NOT_FOUND
        return Response(response_data, status=response_status)


class SessionsDetail(SecureAPIView):
    """
    **Use Case**

        SessionsDetail gets a details about a specific API session, as well as
        enables you to delete an API session.


    **Example Requests**

        GET /api/session/{session_id}

        DELETE /api/session/{session_id}/delete

    **GET Response Values**

        * token: A unique token value for the session.
        * expires: The number of seconds until the session expires.
        * user_id: The unique user identifier.
        * uri: The URI to use to get details about the session.
    """

    def get(self, request, session_id):
        response_data = {}
        base_uri = generate_base_uri(request)
        session_store = _get_session_store(session_id)
        try:
            user_id = session_store[SESSION_KEY]
            backend_path = session_store[BACKEND_SESSION_KEY]
            backend = load_backend(backend_path)
            user = backend.get_user(user_id) or AnonymousUser()
        except KeyError:
            user = AnonymousUser()
        if not user.is_authenticated():
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        response_data['token'] = session_store.session_key
        response_data['expires'] = session_store.get_expiry_age()
        response_data['uri'] = base_uri
        response_data['user_id'] = user.id
        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, session_id):
        session_store = _get_session_store(session_id)
        if session_store is None or not SESSION_KEY in session_store:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        user_id = session_store[SESSION_KEY]
        session_store.flush()
        if request.user is not None and not request.user.is_anonymous():
            logout(request)
        AUDIT_LOG.info(u"API::User session terminated for user-id - {0}".format(user_id))
        return Response({}, status=status.HTTP_204_NO_CONTENT)
