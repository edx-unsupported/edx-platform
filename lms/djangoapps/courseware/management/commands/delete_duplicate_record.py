"""
Script for deleting duplicate record in courseModuleCompletion table
for a specific course_id and for a specific content_id and
for a specific username.
"""

from django.core.management.base import BaseCommand, CommandError
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from util.prompt import query_yes_no
from progress.models import CourseModuleCompletion
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Command class for course reference removal
    """

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        """
        This handler operation does the actual work!
        """
        if len(args) != 3:
            raise CommandError("delete_record requires exactly three arguments: <course_id> |<content_id>| |username|")
        try:
            course_key = CourseKey.from_string(args[0])
        except InvalidKeyError:
            raise Exception("Invalid course key")

        content_id = args[1]
        username = args[2]
        if username:
            try:
                user_id = User.objects.get(username=username).pk
            except User.DoesNotExist:
                raise Exception("User does not exists with the given username")

            if content_id:
                if query_yes_no("Deleting Duplicate records with references to course {0} and content {1} and"
                                " username {2}. Confirm?".format(course_key, content_id, username), default="no"):
                    if query_yes_no("Are you sure. This action cannot be undone!", default="no"):
                        course_modules = CourseModuleCompletion.objects.filter(
                            user_id=user_id,
                            course_id=course_key,
                            content_id=content_id,
                        )
                        if course_modules and len(course_modules) > 1:
                            [course_module.delete() for course_module in course_modules]
                            print('Duplicate records deleted!')
                        else:
                            print('No duplicates records exists')
