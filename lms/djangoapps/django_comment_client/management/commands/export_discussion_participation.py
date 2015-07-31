""" Management command to export discussion participation statistics per course to csv """
import csv
import dateutil
from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from courseware.courses import get_course
from student.models import CourseEnrollment

from lms.lib.comment_client.user import User
import django_comment_client.utils as utils


class _Fields:
    """ Container class for field names """
    USER_ID = u"id"
    USERNAME = u"username"
    EMAIL = u"email"
    FIRST_NAME = u"first_name"
    LAST_NAME = u"last_name"
    THREADS = u"num_threads"
    COMMENTS = u"num_comments"
    REPLIES = u"num_replies"
    UPVOTES = u"num_upvotes"
    FOLOWERS = u"num_thread_followers"
    COMMENTS_GENERATED = u"num_comments_generated"


def _make_social_stats(threads=0, comments=0, replies=0, upvotes=0, followers=0, comments_generated=0):
    """ Builds social stats with values specified """
    return {
        _Fields.THREADS: threads,
        _Fields.COMMENTS: comments,
        _Fields.REPLIES: replies,
        _Fields.UPVOTES: upvotes,
        _Fields.FOLOWERS: followers,
        _Fields.COMMENTS_GENERATED: comments_generated,
    }


class Command(BaseCommand):
    """
    Exports discussion participation per course

    Usage:
        ./manage.py lms export_discussion_participation course_key [dest_file] [OPTIONS]

        * course_key - target course key (e.g. edX/DemoX/T1)
        * dest_file - location of destination file (created if missing, overwritten if exists)

    OPTIONS:

        * thread-type - one of {discussion, question}. Filters discussion participation stats by discussion thread type.
        * end-date - date time in iso8601 format (YYYY-MM-DD hh:mm:ss). Filters discussion participation stats
          by creation date: no threads/comments/replies created *after* this date is included in calculation

    Examples:

    * `./manage.py lms export_discussion_participation <course_key>` - exports entire discussion participation stats for
        a course; output is written to default location (same folder, auto-generated file name)
    * `./manage.py lms export_discussion_participation <course_key> <file_name>` - exports entire discussion
        participation stats for a course; output is written chosen file (created if missing, overwritten if exists)
    * `./manage.py lms export_discussion_participation <course_key> --thread-type=[discussion|question]` - exports
        discussion participation stats for a course for chosen thread type only.
    * `./manage.py lms export_discussion_participation <course_key> --end-date=<iso8601 datetime>` - exports discussion
        participation stats for a course for threads/comments/replies created before specified date.
    * `./manage.py lms export_discussion_participation <course_key> --end-date=<iso8601 datetime>
        --thread-type=[discussion|question]` - exports discussion participation stats for a course for
        threads/comments/replies created before specified date, including only threads of specified type
    """
    THREAD_TYPE_PARAMETER = 'thread_type'
    END_DATE_PARAMETER = 'end_date'

    args = "<course_id> <output_file_location>"

    option_list = BaseCommand.option_list + (
        make_option(
            '--thread-type',
            action='store',
            type='choice',
            dest=THREAD_TYPE_PARAMETER,
            choices=('discussion', 'question'),
            default=None,
            help='Filter threads, comments and replies by thread type'
        ),
        make_option(
            '--end-date',
            action='store',
            type='string',
            dest=END_DATE_PARAMETER,
            default=None,
            help='Include threads, comments and replies created before the supplied date (iso8601 format)'
        ),
    )

    row_order = [
        _Fields.USERNAME, _Fields.EMAIL, _Fields.FIRST_NAME, _Fields.LAST_NAME, _Fields.USER_ID,
        _Fields.THREADS, _Fields.COMMENTS, _Fields.REPLIES,
        _Fields.UPVOTES, _Fields.FOLOWERS, _Fields.COMMENTS_GENERATED
    ]

    def _get_users(self, course_key):
        """ Returns users enrolled to a course as dictionary user_id => user """
        users = CourseEnrollment.users_enrolled_in(course_key)
        return {user.id: user for user in users}

    def _get_social_stats(self, course_key, end_date=None, thread_type=None):
        """ Gets social stats for course with specified filter parameters """
        date = dateutil.parser.parse(end_date) if end_date else None
        return {
            int(user_id): data for user_id, data
            in User.all_social_stats(str(course_key), end_date=date, thread_type=thread_type).iteritems()
        }

    def _merge_user_data_and_social_stats(self, userdata, social_stats):
        """ Merges user data (email, username, etc.) and discussion stats """
        result = []
        for user_id, user in userdata.iteritems():
            user_record = {
                _Fields.USER_ID: user.id,
                _Fields.USERNAME: user.username,
                _Fields.EMAIL: user.email,
                _Fields.FIRST_NAME: user.first_name,
                _Fields.LAST_NAME: user.last_name,
            }
            stats = social_stats.get(user_id, _make_social_stats())
            result.append(utils.merge_dict(user_record, stats))
        return result

    def _output(self, data, output_stream):
        """ Exports data in csv format to specified output stream """
        csv_writer = csv.DictWriter(output_stream, self.row_order)
        csv_writer.writeheader()
        for row in sorted(data, key=lambda item: item['username']):
            to_write = {key: value for key, value in row.items() if key in self.row_order}
            csv_writer.writerow(to_write)

    def _get_filter_string_representation(self, options):
        """ Builds human-readable filter parameters representation """
        filter_strs = []
        if options.get(self.THREAD_TYPE_PARAMETER, None):
            filter_strs.append("Thread type:{}".format(options[self.THREAD_TYPE_PARAMETER]))
        if options.get(self.END_DATE_PARAMETER, None):
            filter_strs.append("Created before:{}".format(options[self.END_DATE_PARAMETER]))
        return ", ".join(filter_strs) if filter_strs else "all"

    def get_default_file_location(self, course_key):
        """ Builds default destination file name """
        return utils.format_filename(
            "social_stats_{course}_{date:%Y_%m_%d_%H_%M_%S}.csv".format(course=course_key, date=datetime.utcnow())
        )

    def handle(self, *args, **options):
        """ Executes command """
        if not args:
            raise CommandError("Course id not specified")
        if len(args) > 2:
            raise CommandError("Only one course id may be specified")
        raw_course_key = args[0]

        if len(args) == 1:
            output_file_location = self.get_default_file_location(raw_course_key)
        else:
            output_file_location = args[1]

        try:
            course_key = CourseKey.from_string(raw_course_key)
        except InvalidKeyError:
            course_key = SlashSeparatedCourseKey.from_deprecated_string(raw_course_key)

        course = get_course(course_key)
        if not course:
            raise CommandError("Invalid course id: {}".format(course_key))

        users = self._get_users(course_key)
        social_stats = self._get_social_stats(
            course_key,
            end_date=options.get(self.END_DATE_PARAMETER, None),
            thread_type=options.get(self.THREAD_TYPE_PARAMETER, None)
        )
        merged_data = self._merge_user_data_and_social_stats(users, social_stats)

        filter_str = self._get_filter_string_representation(options)

        self.stdout.write("Writing social stats ({filters}) to {file}\n".format(
            filters=filter_str, file=output_file_location
        ))
        with open(output_file_location, 'wb') as output_stream:
            self._output(merged_data, output_stream)

        self.stdout.write("Success!\n")