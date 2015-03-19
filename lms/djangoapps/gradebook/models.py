"""
Django database models supporting the gradebook app
"""
from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Max, Min, Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from model_utils.models import TimeStampedModel
from student.models import CourseEnrollment
from xmodule_django.models import CourseKeyField


class StudentGradebook(TimeStampedModel):
    """
    StudentGradebook is essentiall a container used to cache calculated
    grades (see courseware.grades.grade), which can be an expensive operation.
    """
    user = models.ForeignKey(User, db_index=True)
    course_id = CourseKeyField(db_index=True, max_length=255, blank=True)
    grade = models.FloatField()
    proforma_grade = models.FloatField()

    class Meta:
        """
        Meta information for this Django model
        """
        unique_together = (('user', 'course_id'),)

    @classmethod
    def generate_leaderboard(cls, course_key, user_id=None, count=3, exclude_users=[]):
        """
        Assembles a data set representing the Top N users, by grade, for a given course.
        Optionally provide a user_id to include user-specific info.  For example, you
        may want to view the Top 5 users, but also need the data for the logged-in user
        who may actually be currently located in position #10.

        data = {
            'course_avg': 0.873,
            'queryset': [
                {'id': 123, 'username': 'testuser1', 'title', 'Engineer', 'avatar_url': 'http://gravatar.com/123/', 'grade': 0.92, 'created': '2014-01-15 06:27:54'},
                {'id': 983, 'username': 'testuser2', 'title', 'Analyst', 'avatar_url': 'http://gravatar.com/983/', 'grade': 0.91, 'created': '2014-06-27 01:15:54'},
                {'id': 246, 'username': 'testuser3', 'title', 'Product Owner', 'avatar_url': 'http://gravatar.com/246/', 'grade': 0.90, 'created': '2014-03-19 04:54:54'},
                {'id': 357, 'username': 'testuser4', 'title', 'Director', 'avatar_url': 'http://gravatar.com/357/', 'grade': 0.89, 'created': '2014-12-01 08:38:54'},
            ]
            ### IF USER ID SPECIFIED (in this case user_id=246) ###
            'user_position': 4,
            'user_grade': 0.89
        }

        If there is a discrepancy between the number of gradebook entries and the overall number of enrolled
        users (excluding any users who should be excluded), then we modify the course average to account for
        those users who currently lack gradebook entries.  We assume zero grades for these users because they
        have not yet submitted a response to a scored assessment which means no grade has been calculated.
        """
        data = {}
        data['course_avg'] = 0
        data['course_max'] = 0
        data['course_min'] = 0
        data['course_count'] = 0
        data['queryset'] = []

        enrolled_users_not_excluded = CourseEnrollment.users_enrolled_in(course_key).exclude(id__in=exclude_users)
        total_user_count = enrolled_users_not_excluded.count()

        if total_user_count:
            # Generate the base data set we're going to work with
            queryset = StudentGradebook.objects.select_related('user')\
                .filter(course_id__exact=course_key, user__is_active=True, user__in=enrolled_users_not_excluded)
            gradebook_user_count = len(queryset)

            if gradebook_user_count:
                # Calculate the class average
                course_avg = queryset.aggregate(Avg('grade'))['grade__avg']
                if course_avg is not None:
                    # Take into account any ungraded students (assumes zeros for grades...)
                    course_avg = course_avg / total_user_count * gradebook_user_count

                    # Fill up the response container
                    data['course_avg'] = float("{0:.3f}".format(course_avg))
                    data['course_max'] = queryset.aggregate(Max('grade'))['grade__max']
                    data['course_min'] = queryset.aggregate(Min('grade'))['grade__min']
                    data['course_count'] = queryset.aggregate(Count('grade'))['grade__count']

                # Construct the leaderboard as a queryset
                data['queryset'] = queryset.values(
                    'user__id',
                    'user__username',
                    'user__profile__title',
                    'user__profile__avatar_url',
                    'grade',
                    'modified')\
                    .order_by('-grade', 'modified')[:count]
                # If a user_id value was provided, we need to provide some additional user-specific data to the caller
                if user_id:
                    user_grade = 0
                    user_time_scored = timezone.now()
                    try:
                        user_queryset = StudentGradebook.objects.get(course_id__exact=course_key, user__id=user_id)
                    except StudentGradebook.DoesNotExist:
                        user_queryset = None
                    if user_queryset:
                        user_grade = user_queryset.grade
                        user_time_scored = user_queryset.created
                    users_above = queryset.filter(grade__gte=user_grade)\
                        .exclude(user__id=user_id)\
                        .exclude(grade=user_grade, modified__gt=user_time_scored)
                    data['user_position'] = len(users_above) + 1
                    data['user_grade'] = user_grade

        return data


class StudentGradebookHistory(TimeStampedModel):
    """
    A running audit trail for the StudentGradebook model.  Listens for
    post_save events and creates/stores copies of gradebook entries.
    """
    user = models.ForeignKey(User, db_index=True)
    course_id = CourseKeyField(db_index=True, max_length=255, blank=True)
    grade = models.FloatField()
    proforma_grade = models.FloatField()

    @receiver(post_save, sender=StudentGradebook)
    def save_history(sender, instance, **kwargs):  # pylint: disable=no-self-argument, unused-argument
        """
        Event hook for creating gradebook entry copies
        """
        history_entry = StudentGradebookHistory(
            user=instance.user,
            course_id=instance.course_id,
            grade=instance.grade,
            proforma_grade=instance.proforma_grade
        )
        history_entry.save()
