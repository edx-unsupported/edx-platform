"""
Signal handlers supporting various gradebook use cases
"""
from django.dispatch import receiver

from util.signals import course_deleted

from progress.models import CourseModuleCompletion, StudentProgress, StudentProgressHistory


@receiver(course_deleted)
def on_course_deleted(sender, **kwargs):  # pylint: disable=W0613
    """
    Listens for a 'course_deleted' signal and when observed
    removes model entries for the specified course
    """
    course_key = kwargs['course_key']
    CourseModuleCompletion.objects.filter(course_id=unicode(course_key)).delete()
    StudentProgress.objects.filter(course_id=course_key).delete()
    StudentProgressHistory.objects.filter(course_id=course_key).delete()
