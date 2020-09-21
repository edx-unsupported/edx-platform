""" Module containing a task for user progress migration """

from celery.task import task
from completion.models import BlockCompletion
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from courseware.models import StudentModule
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from student.models import AnonymousUserId, anonymous_id_for_user, CourseEnrollment
from submissions.models import StudentItem


# TODO: Add i18n
OUTCOME_SOURCE_NOT_FOUND = 'source email not found'
OUTCOME_SOURCE_NOT_ENROLLED = 'source email not enrolled in given course'
OUTCOME_TARGET_NOT_FOUND = 'target email not found'
OUTCOME_TARGET_ALREADY_ENROLLED = 'target email already enrolled in given course'
OUTCOME_COURSE_NOT_FOUND = 'course key not found'
OUTCOME_FAILED_MIGRATION = 'failed to migrate progress'
OUTCOME_MIGRATED = 'migrated'


@task(bind=True)
def merge_completions(self, merge_list, result_recipients=None):
    ''' Task that migrates progress from one user to another '''
    if not result_recipients:
        # TODO Get from settings
        pass

    # Starting migrating completions for each entry
    results = [{
        'course': course,
        'source_email': source,
        'dest_email': target,
        'outcome': _migrate_completions(course, source, target)
    } for (course, source, target) in merge_list]

    # TODO Generate output csv
    # TODO Save CSV and send email notifying recipients


def _migrate_completions(course, source, target):
    ''' Helper that migrates completions from one user to another '''
    try:
        course_key = CourseKey.from_string(course)
    except InvalidKeyError:
        return OUTCOME_COURSE_NOT_FOUND

    try:
        source = User.objects.get(email=source)
    except ObjectDoesNotExist:
        return OUTCOME_SOURCE_NOT_FOUND

    try:
        enrollment = CourseEnrollment.objects.get(user=source, course=course_key)
    except ObjectDoesNotExist:
        return OUTCOME_SOURCE_NOT_ENROLLED

    try:
        target = User.objects.get(email=target)
    except ObjectDoesNotExist:
        return OUTCOME_TARGET_NOT_FOUND

    try:
        assert not CourseEnrollment.objects.get(user=target, course=course_key)
    except AssertionError:
        return OUTCOME_TARGET_ALREADY_ENROLLED
    except ObjectDoesNotExist:
        pass

    # Fetch completions for source user
    completions = BlockCompletion.user_course_completion_queryset(user=source, course_key=course_key)

    # Fetch edx-submissions data for source user
    anonymous_ids = AnonymousUserId.objects.filter(user=source, course_id=course_key).values('anonymous_user_id')
    submissions = StudentItem.objects.filter(course_id=course_key, student_id__in=anonymous_ids)

    # Fetch StudentModule table data for source user
    student_states = StudentModule.objects.filter(student=source, course_id=course_key)

    # Actually migrate completions and progress
    try:
        with transaction.atomic():
            # Modify enrollment
            enrollment.user = target
            enrollment.save()
            # Migrate completions for user
            for completion in completions:
                completion.user = target
                completion.save()
            # Migrate edx-submissions
            for submission in submissions:
                submission.student_id = anonymous_id_for_user(target, course_key)
                submission.save()
            # Migrate StudentModule
            for state in student_states:
                state.student = target
                state.save()
    except Exception:  # TODO Replace broad Exception
        return OUTCOME_FAILED_MIGRATION

    return OUTCOME_MIGRATED
