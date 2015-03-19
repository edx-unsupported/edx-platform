"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/api_manager/management/commands/tests/test_migrate_orgdata.py]
"""
from datetime import datetime
import uuid

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.test.utils import override_settings

from api_manager import models as api_models
from api_manager.management.commands import migrate_courseids_v2
from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
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


    def test_migrate_courseids_v2(self):
        """
        Test the data migration
        """
        # Set up the data to be migrated
        user = User.objects.create(email='testuser@edx.org', username='testuser', password='testpassword', is_active=True)
        group = Group.objects.create(name='Test Group')
        group_profile = api_models.GroupProfile.objects.create(group=group)
        course_group = api_models.CourseGroupRelationship.objects.create(course_id=self.old_style_course_id, group=group)
        course_content_group = api_models.CourseContentGroupRelationship.objects.create(course_id=self.old_style_course_id, content_id=self.old_style_content_id, group_profile=group_profile)
        course_module_completion = api_models.CourseModuleCompletion.objects.create(user=user, course_id=self.old_style_course_id, content_id=self.old_style_content_id)

        user2 = User.objects.create(email='testuser2@edx.org', username='testuser2', password='testpassword2', is_active=True)
        group2 = Group.objects.create(name='Test Group2')
        group_profile2 = api_models.GroupProfile.objects.create(group=group2)
        course_group2 = api_models.CourseGroupRelationship.objects.create(course_id=self.new_style_course_id2, group=group2)
        course_content_group2 = api_models.CourseContentGroupRelationship.objects.create(course_id=self.new_style_course_id2, content_id=self.new_style_content_id2, group_profile=group_profile2)
        course_module_completion2 = api_models.CourseModuleCompletion.objects.create(user=user2, course_id=self.new_style_course_id2, content_id=self.new_style_content_id2)


        # Run the data migration
        migrate_courseids_v2.Command().handle()


        # Confirm that the data has been properly migrated
        updated_course_group = api_models.CourseGroupRelationship.objects.get(id=course_group.id)
        self.assertEqual(updated_course_group.course_id, self.old_style_course_id)
        updated_course_group = api_models.CourseGroupRelationship.objects.get(id=course_group2.id)
        self.assertEqual(updated_course_group.course_id, self.old_style_course_id2)
        print "Course Group Data Migration Passed"

        updated_course_content_group = api_models.CourseContentGroupRelationship.objects.get(id=course_content_group.id)
        self.assertEqual(updated_course_content_group.course_id, self.old_style_course_id)
        self.assertEqual(updated_course_content_group.content_id, self.old_style_content_id)
        updated_course_content_group = api_models.CourseContentGroupRelationship.objects.get(id=course_content_group2.id)
        self.assertEqual(updated_course_content_group.course_id, self.old_style_course_id2)
        self.assertEqual(updated_course_content_group.content_id, self.old_style_content_id2)
        print "Course Content Group Data Migration Passed"

        updated_course_module_completion = api_models.CourseModuleCompletion.objects.get(id=course_module_completion.id)
        self.assertEqual(updated_course_module_completion.course_id, self.old_style_course_id)
        self.assertEqual(updated_course_module_completion.content_id, self.old_style_content_id)
        updated_course_module_completion = api_models.CourseModuleCompletion.objects.get(id=course_module_completion2.id)
        self.assertEqual(updated_course_module_completion.course_id, self.old_style_course_id2)
        self.assertEqual(updated_course_module_completion.content_id, self.old_style_content_id2)
        print "Course Module Completion Data Migration Passed"
