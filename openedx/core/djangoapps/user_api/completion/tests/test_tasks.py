"""Unit tests for merging user progress module"""

from django.contrib.auth.models import User
from django.core import mail


from openedx.core.djangoapps.user_api.completion.tasks import (
    OUTCOME_COURSE_KEY_INVALID,
    OUTCOME_COURSE_NOT_FOUND,
    OUTCOME_FAILED_MIGRATION,
    OUTCOME_MIGRATED,
    OUTCOME_SOURCE_NOT_ENROLLED,
    OUTCOME_SOURCE_NOT_FOUND,
    OUTCOME_TARGET_ALREADY_ENROLLED,
    OUTCOME_TARGET_NOT_FOUND,
    migrate_progress,
    _create_results_csv,
    _migrate_progress,
)
from student.models import CourseEnrollment
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from mock import patch
import uuid


class ProgressMigrationTestCase(ModuleStoreTestCase):
    """
    Parent test case for progress migration tests.
    """

    def setUp(self):
        super(ProgressMigrationTestCase, self).setUp()
        self.course = CourseFactory.create(
            org='org', course='course', number='number'
        )
        self.course_id = str(self.course.id)

    def _create_user(self, username=None, enrolled=None):
        """
        Shortcut to create users and enroll them in some course.
        """

        if not username:
            username = uuid.uuid4().hex.upper()[0:6]
        user = User.objects.create(
            username=username,
            email="{}@example.com".format(username)
        )
        if enrolled:
            CourseEnrollment.enroll(user, self.course.id, mode='audit')
        return user

    def test_course_invalid_key(self):
        source = self._create_user(enrolled=self.course)
        target = self._create_user()
        self.assertEqual(
            _migrate_progress('a+b+c', source.email, target.email),
            OUTCOME_COURSE_KEY_INVALID
        )

    def test_course_not_found(self):
        source = self._create_user(enrolled=self.course)
        target = self._create_user()
        self.assertEqual(
            _migrate_progress(self.course_id + 'abc', source.email, target.email),
            OUTCOME_COURSE_NOT_FOUND
        )

    def test_source_not_found(self):
        target = self._create_user()
        self.assertEqual(
            _migrate_progress(self.course_id, 'dummy@example.com', target.email),
            OUTCOME_SOURCE_NOT_FOUND
        )

    def test_source_not_enrolled(self):
        source = self._create_user()
        target = self._create_user()
        self.assertEqual(
            _migrate_progress(self.course_id, source.email, target.email),
            OUTCOME_SOURCE_NOT_ENROLLED
        )

    def test_target_not_found(self):
        source = self._create_user(enrolled=self.course)
        self.assertEqual(
            _migrate_progress(self.course_id, source.email, 'dummy@example.com'),
            OUTCOME_TARGET_NOT_FOUND
        )

    def test_target_already_enrolled(self):
        source = self._create_user(enrolled=self.course)
        target = self._create_user(enrolled=self.course)
        self.assertEqual(
            _migrate_progress(self.course_id, source.email, target.email),
            OUTCOME_TARGET_ALREADY_ENROLLED
        )

    def test_migrated(self):
        source = self._create_user(enrolled=self.course)
        target = self._create_user()
        self.assertEqual(
            _migrate_progress(self.course_id, source.email, target.email),
            OUTCOME_MIGRATED
        )

    def test_failed_migration(self):
        source = self._create_user(enrolled=self.course)
        target = self._create_user()
        with patch.object(CourseEnrollment, 'save') as mock:
            mock.side_effect = Exception('Failed to save')
            self.assertEqual(
                _migrate_progress(self.course_id, source.email, target.email),
                OUTCOME_FAILED_MIGRATION
            )

    def test_migrate_progress(self):
        result_csv_rows = [
            {
                'course': self.course_id + 'abc',
                'source_email': self._create_user(enrolled=self.course).email,
                'dest_email': self._create_user().email,
                'outcome': OUTCOME_COURSE_NOT_FOUND
            },
            {
                'course': self.course_id,
                'source_email': self._create_user(enrolled=self.course).email,
                'dest_email': self._create_user(enrolled=self.course).email,
                'outcome': OUTCOME_TARGET_ALREADY_ENROLLED
            },
            {
                'course': self.course_id,
                'source_email': self._create_user(enrolled=self.course).email,
                'dest_email': self._create_user().email,
                'outcome': OUTCOME_MIGRATED
            },
        ]

        migrate_list = [
            (row['course'], row['source_email'], row['dest_email'])
            for row
            in result_csv_rows
        ]

        results_csv = migrate_progress(migrate_list, ['dummy@example.com'])

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.subject, u'Progress migration result')
        self.assertEqual(message.body, u'Migration is finished. Please review this email attachment.')

        attachments = message.attachments
        self.assertEqual(len(attachments), 1)

        attachment_content = attachments[0][1]
        self.assertEqual(attachment_content, _create_results_csv(result_csv_rows))
