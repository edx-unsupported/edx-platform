"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/api_manager/management/commands/tests/test_migrate_orgdata.py]
"""
from datetime import datetime
import uuid

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.test.utils import override_settings

from projects.management.commands import migrate_project_courseids_v2
from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
from projects.models import Project, Workgroup, WorkgroupReview, WorkgroupPeerReview, WorkgroupSubmission, WorkgroupSubmissionReview
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory

from django.db import connection

@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
class MigrateCourseIdsTests(TestCase):
    """
    Test suite for data migration script
    """

    def setUp(self):

        self.course = CourseFactory.create(
            start=datetime(2014, 6, 16, 14, 30),
            end=datetime(2015, 1, 16)
        )
        self.test_data = '<html>{}</html>'.format(str(uuid.uuid4()))

        self.chapter = ItemFactory.create(
            category="chapter",
            parent_location=self.course.location,
            data=self.test_data,
            due=datetime(2014, 5, 16, 14, 30),
            display_name="Overview"
        )

        self.old_style_course_id = self.course.id.to_deprecated_string()
        self.new_style_course_id = unicode(self.course.id)
        self.old_style_content_id = self.chapter.location.to_deprecated_string()
        self.new_style_content_id = unicode(self.chapter.location)

        self.course2 = CourseFactory.create(
            org='TEST',
            start=datetime(2014, 6, 16, 14, 30),
            end=datetime(2015, 1, 16)
        )
        self.chapter2 = ItemFactory.create(
            category="chapter",
            parent_location=self.course2.location,
            data=self.test_data,
            due=datetime(2014, 5, 16, 14, 30),
            display_name="Overview"
        )

        self.old_style_course_id2 = self.course2.id.to_deprecated_string()
        self.new_style_course_id2 = unicode(self.course2.id)
        self.old_style_content_id2 = self.chapter2.location.to_deprecated_string()
        self.new_style_content_id2 = unicode(self.chapter2.location)


    def test_migrate_project_courseids_v2(self):
        """
        Test the data migration
        """
        # Set up the data to be migrated
        user = User.objects.create(email='testuser@edx.org', username='testuser', password='testpassword', is_active=True)
        reviewer = User.objects.create(email='testreviewer@edx.org', username='testreviewer', password='testpassword', is_active=True)
        project = Project.objects.create(course_id=self.old_style_course_id, content_id=self.old_style_content_id)
        workgroup = Workgroup.objects.create(name='Test Workgroup', project=project)
        workgroup_review = WorkgroupReview.objects.create(workgroup=workgroup, content_id=self.old_style_content_id)
        workgroup_peer_review = WorkgroupPeerReview.objects.create(workgroup=workgroup, user=user, reviewer=reviewer, question="Question?", answer="Answer!", content_id=self.new_style_content_id)
        workgroup_submission = WorkgroupSubmission.objects.create(workgroup=workgroup, user=user)
        workgroup_submission_review = WorkgroupSubmissionReview.objects.create(submission=workgroup_submission, content_id=self.old_style_content_id)

        user2 = User.objects.create(email='testuser2@edx.org', username='testuser2', password='testpassword2', is_active=True)
        reviewer2 = User.objects.create(email='testreviewer2@edx.org', username='testreviewer2', password='testpassword', is_active=True)
        project2 = Project.objects.create(course_id=self.new_style_course_id2, content_id=self.new_style_content_id2)
        workgroup2 = Workgroup.objects.create(name='Test Workgroup2', project=project2)
        workgroup_review2 = WorkgroupReview.objects.create(workgroup=workgroup2, content_id=self.new_style_content_id2)
        workgroup_peer_review2 = WorkgroupPeerReview.objects.create(workgroup=workgroup2, user=user2, reviewer=reviewer2, question="Question?", answer="Answer!", content_id=self.new_style_content_id2)
        workgroup_submission2 = WorkgroupSubmission.objects.create(workgroup=workgroup2, user=user2)
        workgroup_submission_review2 = WorkgroupSubmissionReview.objects.create(submission=workgroup_submission2, content_id=self.new_style_content_id2)


        # Run the data migration
        migrate_project_courseids_v2.Command().handle()


        # Confirm that the data has been properly migrated
        updated_project = Project.objects.get(id=project.id)
        self.assertEqual(updated_project.course_id, self.old_style_course_id)
        self.assertEqual(updated_project.content_id, self.old_style_content_id)
        updated_project = Project.objects.get(id=project2.id)
        self.assertEqual(updated_project.course_id, self.old_style_course_id2)
        self.assertEqual(updated_project.content_id, self.old_style_content_id2)
        print "Project Data Migration Passed"

        updated_workgroup_review = WorkgroupReview.objects.get(id=workgroup_review.id)
        self.assertEqual(updated_workgroup_review.content_id, self.old_style_content_id)
        updated_workgroup_review = WorkgroupReview.objects.get(id=workgroup_review2.id)
        self.assertEqual(updated_workgroup_review.content_id, self.old_style_content_id2)
        print "Workgroup Review Data Migration Passed"

        updated_workgroup_peer_review = WorkgroupPeerReview.objects.get(id=workgroup_peer_review.id)
        self.assertEqual(updated_workgroup_peer_review.content_id, self.old_style_content_id)
        updated_workgroup_peer_review = WorkgroupPeerReview.objects.get(id=workgroup_peer_review2.id)
        self.assertEqual(updated_workgroup_peer_review.content_id, self.old_style_content_id2)
        print "Workgroup Peer Review Data Migration Passed"

        updated_workgroup_submission_review = WorkgroupSubmissionReview.objects.get(id=workgroup_submission_review.id)
        self.assertEqual(updated_workgroup_submission_review.content_id, self.old_style_content_id)
        updated_workgroup_submission_review = WorkgroupSubmissionReview.objects.get(id=workgroup_submission_review2.id)
        self.assertEqual(updated_workgroup_submission_review.content_id, self.old_style_content_id2)
        print "Workgroup Submission Review Data Migration Passed"
