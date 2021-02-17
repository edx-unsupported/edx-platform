"""
Given a course id and student username, copy the content of database table courseware_studentmodule
for the given course and student and add similar records for all other students registered in that
course who do not have any entry of their own for the given course.

This will just create new responses for users but it would not change the progress or proficiency.

An example usecase could be to copy all the poll responses by a certain user in a given course and
populate database to contain similar responses for all other users registered in that course.
"""


from textwrap import dedent

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

from lms.djangoapps.courseware.models import StudentModule
from student.models import CourseEnrollment
from xmodule.modulestore.django import modulestore


class Command(BaseCommand):
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument('course_id',
                            help='Course ID of course for which you want to add responses')
        parser.add_argument('username',
                            help='Username of user whose responses you want to copy')

    def handle(self, *args, **options):
        store = modulestore()

        try:
            course_key = CourseKey.from_string(options['course_id'])
        except InvalidKeyError:
            raise CommandError("Invalid course_id")
        if store.get_course(course_key) is None:
            raise CommandError("Invalid course_id")

        try:
            user_id = User.objects.get(username=options['username']).id
        except User.DoesNotExist:
            raise CommandError("Invalid username")
        db_entries = StudentModule.objects.filter(student_id=user_id, course_id=course_key).values()
        if not db_entries:
            raise CommandError("User has no entries for this course")

        registerations = CourseEnrollment.objects.filter(course_id=course_key, is_active=True)
        new_entries = []
        for registeration in registerations:
            curr_student_id = registeration.user_id
            if not StudentModule.objects.filter(student_id=curr_student_id, course_id=course_key):
                for entry in db_entries:
                    data = {k: v for k, v in entry.items() if k != 'id'}
                    data['student_id'] = curr_student_id
                    new_entries.append(StudentModule(**data))

        StudentModule.objects.bulk_create(new_entries)

        self.stdout.write(self.style.SUCCESS('Created {} new entries in database'.format(len(new_entries))))
