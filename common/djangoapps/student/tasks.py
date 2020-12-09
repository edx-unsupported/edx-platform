"""
This file contains celery tasks for sending email
"""


import logging

from celery.exceptions import MaxRetriesExceededError
from celery.task import task
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from edx_ace import ace
from edx_ace.errors import RecoverableChannelDeliveryError
from edx_ace.message import Message
from edx_notifications.lib.publisher import bulk_publish_notification_to_users
from mobileapps.models import MobileApp
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.lib.celery.task_utils import emulate_http_request
from student.models import CourseEnrollment

log = logging.getLogger('edx.celery.task')


@task(bind=True)
def send_activation_email(self, msg_string, from_address=None):
    """
    Sending an activation email to the user.
    """
    msg = Message.from_string(msg_string)

    max_retries = settings.RETRY_ACTIVATION_EMAIL_MAX_ATTEMPTS
    retries = self.request.retries

    if from_address is None:
        from_address = configuration_helpers.get_value('ACTIVATION_EMAIL_FROM_ADDRESS') or (
            configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL)
        )
    msg.options['from_address'] = from_address

    dest_addr = msg.recipient.email_address

    site = Site.objects.get_current()
    user = User.objects.get(username=msg.recipient.username)

    try:
        with emulate_http_request(site=site, user=user):
            ace.send(msg)
    except RecoverableChannelDeliveryError:
        log.info('Retrying sending email to user {dest_addr}, attempt # {attempt} of {max_attempts}'.format(
            dest_addr=dest_addr,
            attempt=retries,
            max_attempts=max_retries
        ))
        try:
            self.retry(countdown=settings.RETRY_ACTIVATION_EMAIL_TIMEOUT, max_retries=max_retries)
        except MaxRetriesExceededError:
            log.error(
                'Unable to send activation email to user from "%s" to "%s"',
                from_address,
                dest_addr,
                exc_info=True
            )
    except Exception:
        log.exception(
            'Unable to send activation email to user from "%s" to "%s"',
            from_address,
            dest_addr,
        )
        raise Exception


@task()
def publish_course_notifications_task(course_id, notification_msg, exclude_user_ids=None):  # pylint: disable=invalid-name
    """
    This function will call the edx_notifications api method "bulk_publish_notification_to_users"
    and run as a new Celery task.
    """
    # get the enrolled and active user_id list for this course.
    user_ids = CourseEnrollment.objects.values_list('user_id', flat=True).filter(
        is_active=1,
        course_id=course_id
    )

    try:
        bulk_publish_notification_to_users(user_ids, notification_msg, exclude_user_ids=exclude_user_ids)
        # if we have a course announcement notification publish it to urban airship too
        if notification_msg.msg_type.name == 'open-edx.studio.announcements.new-announcement':
            # fetch all active mobile apps to send notifications to all apps
            mobile_apps = MobileApp.objects.filter(is_active=True)
            for mobile_app in mobile_apps:
                channel_context = {
                    "api_credentials": mobile_app.get_api_keys()
                }
                preferred_channel = mobile_app.get_notification_provider_name()
                if preferred_channel:
                    bulk_publish_notification_to_users(
                        user_ids,
                        notification_msg,
                        exclude_user_ids=exclude_user_ids,
                        preferred_channel=preferred_channel,
                        channel_context=channel_context
                    )
    except Exception as ex:
        # Notifications are never critical, so we don't want to disrupt any
        # other logic processing. So log and continue.
        log.exception(ex)
