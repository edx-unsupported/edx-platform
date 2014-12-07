"""
Signal handlers supporting various gradebook use cases
"""
from django.dispatch import receiver

from courseware.signals import score_changed
from gradebook.tasks import recalculate_user_grade


@receiver(score_changed)
def on_score_changed(sender, **kwargs):
    """
    Listens for a 'score_changed' signal and when observed
    recalculates the specified user's gradebook entry
    """
    user = kwargs['user']
    course_key = kwargs['course_key']
    recalculate_user_grade.delay(user.id, unicode(course_key))





