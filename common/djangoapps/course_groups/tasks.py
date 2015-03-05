"""
This file contains celery tasks for student course enrollment
"""

from celery.task import task
from .models import CourseUserGroup
from edx_notifications.lib.publisher import bulk_publish_notification_to_users
from student.models import CourseEnrollment

@task()
def publish_course_group_notification_task(course_group_id, notification_msg):  # pylint: disable=invalid-name
    """
    This function will call the edx_notifications api method "bulk_publish_notification_to_users"
    and run as a new Celery task in order to broadcast a message to an entire course cohort
    """
    # get the enrolled and active user_id list for this course.
    user_ids = CourseUserGroup.objects.values_list('users', flat=True).filter(
        id=course_group_id
    )
    #user_ids = CourseEnrollment.objects.values_list('user_id', flat=True).filter(
    #    is_active=1,
    #    course_id=course_id,
    #    user__course_groups=course_group_id
    #)
    bulk_publish_notification_to_users(user_ids, notification_msg)
