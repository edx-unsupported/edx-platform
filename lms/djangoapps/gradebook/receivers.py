"""
Signal handlers supporting various gradebook use cases
"""
from django.dispatch import receiver

from courseware import grades
from courseware.views import get_course
from courseware.signals import score_changed
from util.request import RequestMock

from gradebook.models import StudentGradebook


@receiver(score_changed)
def on_score_changed(sender, **kwargs):
    """
    Listens for an 'on_score_changed' signal and when observed
    recalculates the specified user's gradebook entry
    """
    user = kwargs['user']
    course_key = kwargs['course_key']
    course_descriptor = get_course(course_key, depth=None)
    request = RequestMock().get('/')
    request.user = user
    grade_data = grades.grade(user, request, course_descriptor)
    grade = grade_data['percent']
    try:
        gradebook_entry = StudentGradebook.objects.get(user=user, course_id=course_key)
        if gradebook_entry.grade != grade:
            gradebook_entry.grade = grade
            gradebook_entry.save()
    except StudentGradebook.DoesNotExist:
        StudentGradebook.objects.create(user=user, course_id=course_key, grade=grade)
