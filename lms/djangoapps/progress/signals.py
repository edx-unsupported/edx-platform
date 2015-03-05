"""
Signal handlers supporting various progress use cases
"""
import sys
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .models import StudentProgress
from student.roles import get_aggregate_exclusion_user_ids

from edx_notifications.lib.publisher import (
    publish_notification_to_user,
    get_notification_type
)
from edx_notifications.data import NotificationMessage

from progress.models import StudentProgress, StudentProgressHistory, CourseModuleCompletion
log = logging.getLogger(__name__)


@receiver(pre_save, sender=CourseModuleCompletion)
def handle_cmc_pre_save_signal(sender, instance, **kwargs):
    """
    Handle the pre-save ORM event on CourseModuleCompletions
    """

    if settings.FEATURES['NOTIFICATIONS_ENABLED']:
        # If notifications feature is enabled, then we need to get the user's
        # rank before the save is made, so that we can compare it to
        # after the save and see if the position changes
        content_id = unicode(instance.content_id)
        detached_categories = getattr(settings, 'PROGRESS_DETACHED_CATEGORIES', [])
        if not any(category in content_id for category in detached_categories):
            # attach the rank of the user before the save is completed
            instance.presave_leaderboard_rank = StudentProgress.get_user_position(
                instance.course_id,
                instance.user.id,
                get_aggregate_exclusion_user_ids(instance.course_id)
            )['position']


@receiver(post_save, sender=CourseModuleCompletion, dispatch_uid='edxapp.api_manager.post_save_cms')
def handle_cmc_post_save_signal(sender, instance, created, **kwargs):
    """
    Broadcast the progress change event
    """
    content_id = unicode(instance.content_id)
    detached_categories = getattr(settings, 'PROGRESS_DETACHED_CATEGORIES', [])
    if created and not any(category in content_id for category in detached_categories):
        try:
            progress = StudentProgress.objects.get(user=instance.user, course_id=instance.course_id)
            progress.completions += 1
            progress.save()
        except ObjectDoesNotExist:
            progress = StudentProgress(user=instance.user, course_id=instance.course_id, completions=1)
            progress.save()
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error("Exception type: {} with value: {}".format(exc_type, exc_value))


    if settings.FEATURES['NOTIFICATIONS_ENABLED']:
        # now re-compute the position in the leaderboard
        # and see if we have to fire a notification
        content_id = unicode(instance.content_id)
        detached_categories = getattr(settings, 'PROGRESS_DETACHED_CATEGORIES', [])
        if created and not any(category in content_id for category in detached_categories):
            # attach the rank of the user before the save is completed
            leaderboard_rank = StudentProgress.get_user_position(
                instance.course_id,
                instance.user.id,
                get_aggregate_exclusion_user_ids(instance.course_id)
            )['position']

            if leaderboard_rank < getattr(settings, 'LEADERBOARD_SIZE', 3):
                # We are in the leaderboard, so see if our rank changed
                if leaderboard_rank != instance.presave_leaderboard_rank:
                    notification_msg = NotificationMessage(
                        msg_type=get_notification_type(u'open-edx.lms.leaderboard.progress.rank-changed'),
                        namespace=unicode(instance.course_id),
                        payload={
                            '_schema_version': '1',
                            'old_rank': instance.presave_leaderboard_rank,
                            'rank': leaderboard_rank,
                        }
                    )
                    publish_notification_to_user(int(instance.user.id), notification_msg)


@receiver(post_save, sender=StudentProgress)
def save_history(sender, instance, **kwargs):  # pylint: disable=no-self-argument, unused-argument
    """
    Event hook for creating progress entry copies
    """
    history_entry = StudentProgressHistory(
        user=instance.user,
        course_id=instance.course_id,
        completions=instance.completions
    )
    history_entry.save()
