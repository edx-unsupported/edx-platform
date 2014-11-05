"""
This file contains tasks that are designed to perform background operations on student gradebook.
"""

from celery.task import task
from celery.utils.log import get_task_logger

from django.contrib.auth.models import User
from courseware import grades
from courseware.views import get_course
from util.request import RequestMockWithoutMiddleware
from gradebook.models import StudentGradebook
from opaque_keys.edx.locator import CourseLocator

TASK_LOG = get_task_logger(__name__)


@task()
def recalculate_user_grade(user_id, course_id):
    """
    calculates user's grade in a new celery task.
    """
    try:
        TASK_LOG.info('User grade calcuation task in gradebook started')
        course_key = CourseLocator.from_string(course_id)
        course_descriptor = get_course(course_key, depth=None)
        request = RequestMockWithoutMiddleware().get('/')
        user = User.objects.get(pk=user_id)
        request.user = user
        grade_data = grades.grade(user, request, course_descriptor)
        grade = grade_data['percent']
        proforma_grade = grades.calculate_proforma_grade(grade_data, course_descriptor.grading_policy)
        try:
            gradebook_entry = StudentGradebook.objects.get(user=user, course_id=course_key)
            if gradebook_entry.grade != grade:
                gradebook_entry.grade = grade
                gradebook_entry.proforma_grade = proforma_grade
                gradebook_entry.save()
        except StudentGradebook.DoesNotExist:
            StudentGradebook.objects.create(user=user, course_id=course_key, grade=grade, proforma_grade=proforma_grade)

    except Exception as exc:  # pylint: disable=broad-except
        TASK_LOG.error('Task to recalculate user grade failed: %s', unicode(exc))
