"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/api_manager/management/commands/tests/test_migrate_orgdata.py]
"""
from datetime import datetime
from django.test.utils import override_settings
from mock import MagicMock, patch
import uuid
import json

from django.conf import settings

from capa.tests.response_xml_factory import StringResponseXMLFactory
from courseware import module_render
from courseware.model_data import FieldDataCache
from gradebook.management.commands import generate_gradebook_entries
from gradebook.models import StudentGradebook, StudentGradebookHistory
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xmodule.modulestore import EdxJSONEncoder
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase, mixed_store_config
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory


@patch.dict(settings.FEATURES, {'SIGNAL_ON_SCORE_CHANGED': True})
class GenerateGradebookEntriesTests(ModuleStoreTestCase):
    """
    Test suite for grade generation script
    """

    def setUp(self):
        super(GenerateGradebookEntriesTests, self).setUp()
        # Turn off the signalling mechanism temporarily
        with patch.dict(settings.FEATURES, {'SIGNAL_ON_SCORE_CHANGED': False}):

            # Create a couple courses to work with
            self.course = CourseFactory.create(
                start=datetime(2014, 6, 16, 14, 30),
                end=datetime(2020, 1, 16),
                org='GRADEBOOK'
            )
            self.test_data = '<html>{}</html>'.format(str(uuid.uuid4()))

            chapter1 = ItemFactory.create(
                category="chapter",
                parent_location=self.course.location,
                data=self.test_data,
                due=datetime(2014, 5, 16, 14, 30),
                display_name="Overview"
            )

            chapter2 = ItemFactory.create(
                category="chapter",
                parent_location=self.course.location,
                data=self.test_data,
                due=datetime(2014, 5, 16, 14, 30),
                display_name="Overview"
            )
            self.problem = ItemFactory.create(
                parent_location=chapter1.location,
                category='problem',
                data=StringResponseXMLFactory().build_xml(answer='bar'),
                display_name="homework problem 1",
                metadata={'rerandomize': 'always', 'graded': True, 'format': "Homework"}
            )
            self.problem_progress_summary = {
                "url_name": "homework_problem_1",
                "display_name": "homework problem 1",
                "graded": True,
                "format": "Homework",
                "section_total": [0.15, 1.0, False, "homework problem 1", None, None],
                "due": "2014-05-16T14:30:00+00:00",
                "scores": [[0.15, 1.0, True, "homework problem 1",
                            unicode(self.problem.location), "2014-05-16T14:30:00+00:00"]]
            }
            self.problem_grade_summary = {
                "category": "Homework",
                "percent": 0.15,
                "detail": "Homework 1 - homework problem 1 - 15% (0.15/1)",
                "label": "HW 01"
            }
            self.problem2 = ItemFactory.create(
                parent_location=chapter2.location,
                category='problem',
                data=StringResponseXMLFactory().build_xml(answer='bar'),
                display_name="homework problem 2",
                metadata={'rerandomize': 'always', 'graded': True, 'format': "Homework"}
            )
            self.problem3 = ItemFactory.create(
                parent_location=chapter2.location,
                category='problem',
                data=StringResponseXMLFactory().build_xml(answer='bar'),
                display_name="lab problem 1",
                metadata={'rerandomize': 'always', 'graded': True, 'format': "Lab"}
            )
            self.problem4 = ItemFactory.create(
                parent_location=chapter2.location,
                category='problem',
                data=StringResponseXMLFactory().build_xml(answer='bar'),
                display_name="midterm problem 2",
                metadata={'rerandomize': 'always', 'graded': True, 'format': "Midterm Exam"}
            )
            self.problem5 = ItemFactory.create(
                parent_location=chapter2.location,
                category='problem',
                data=StringResponseXMLFactory().build_xml(answer='bar'),
                display_name="final problem 2",
                metadata={'rerandomize': 'always', 'graded': True, 'format': "Final Exam"}
            )
            self.grading_policy = {
                "GRADER": [{
                    "short_label": "HW",
                    "min_count": 12,
                    "type": "Homework",
                    "drop_count": 2,
                    "weight": 0.15
                }, {
                    "min_count": 12,
                    "type": "Lab",
                    "drop_count": 2,
                    "weight": 0.15
                }, {
                    "short_label": "Midterm",
                    "min_count": 1,
                    "type": "Midterm Exam",
                    "drop_count": 0,
                    "weight": 0.3
                }, {
                    "short_label": "Final",
                    "min_count": 1,
                    "type": "Final Exam",
                    "drop_count": 0,
                    "weight": 0.4
                }],
                "GRADE_CUTOFFS": {"Pass": 0.5}
            }
            # Create some users and enroll them
            self.users = [UserFactory.create(username="testuser" + str(__), profile='test') for __ in xrange(2)]
            self.users.insert(0, self.user)
            for user in self.users:
                CourseEnrollmentFactory.create(user=user, course_id=self.course.id)

                grade = 0.15 * user.id
                module = self.get_module_for_user(user, self.course, self.problem)
                grade_dict = {'value': grade, 'max_value': 1, 'user_id': user.id}
                module.system.publish(module, 'grade', grade_dict)

                grade = 0.20 * user.id
                module = self.get_module_for_user(user, self.course, self.problem2)
                grade_dict = {'value': grade, 'max_value': 1, 'user_id': user.id}
                module.system.publish(module, 'grade', grade_dict)

                grade = 0.25 * user.id
                module = self.get_module_for_user(user, self.course, self.problem3)
                grade_dict = {'value': grade, 'max_value': 1, 'user_id': user.id}
                module.system.publish(module, 'grade', grade_dict)

                grade = 0.30 * user.id
                module = self.get_module_for_user(user, self.course, self.problem4)
                grade_dict = {'value': grade, 'max_value': 1, 'user_id': user.id}
                module.system.publish(module, 'grade', grade_dict)

                grade = 0.33 * user.id
                module = self.get_module_for_user(user, self.course, self.problem5)
                grade_dict = {'value': grade, 'max_value': 1, 'user_id': user.id}
                module.system.publish(module, 'grade', grade_dict)

    def get_module_for_user(self, user, course, problem):
        """Helper function to get useful module at self.location in self.course_id for user"""
        mock_request = MagicMock()
        mock_request.user = user
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            course.id, user, course, depth=2)

        return module_render.get_module(  # pylint: disable=protected-access
            user,
            mock_request,
            problem.location,
            field_data_cache,
        )._xmodule

    @patch.dict(settings.FEATURES, {
        'ALLOW_STUDENT_STATE_UPDATES_ON_CLOSED_COURSE': False,
        'SIGNAL_ON_SCORE_CHANGED': False
    })
    def test_generate_gradebook_entries(self):
        """
        Test the gradebook entry generator
        """
        # Set up the command context
        course_ids = '{},bogus/course/id'.format(self.course.id)
        user_ids = '{}'.format(self.users[0].id)
        current_entries = StudentGradebook.objects.all()
        self.assertEqual(len(current_entries), 0)
        current_entries = StudentGradebookHistory.objects.all()
        self.assertEqual(len(current_entries), 0)

        # Run the command just for one user
        generate_gradebook_entries.Command().handle(user_ids=user_ids)

        # Confirm the gradebook has been properly updated
        current_entries = StudentGradebook.objects.all()
        self.assertEqual(len(current_entries), 1)
        current_entries = StudentGradebookHistory.objects.all()
        self.assertEqual(len(current_entries), 1)
        user0_entry = StudentGradebook.objects.get(user=self.users[0])
        self.assertEqual(user0_entry.grade, 0.24)
        self.assertEqual(user0_entry.proforma_grade, 0.28575)

        # Enable the signaling mechanism
        settings._wrapped.default_settings.FEATURES['SIGNAL_ON_SCORE_CHANGED'] = True

        # Change the score of the final exam for that user
        grade = 0.99
        module = self.get_module_for_user(self.users[0], self.course, self.problem5)
        grade_dict = {'value': grade, 'max_value': 1, 'user_id': self.users[0].id}
        module.system.publish(module, 'grade', grade_dict)

        # Confirm the gradebook has been properly updated
        current_entries = StudentGradebook.objects.all()
        self.assertEqual(len(current_entries), 1)
        current_entries = StudentGradebookHistory.objects.all()
        self.assertEqual(len(current_entries), 2)
        user0_entry = StudentGradebook.objects.get(user=self.users[0])
        self.assertEqual(user0_entry.grade, 0.50)
        self.assertEqual(user0_entry.proforma_grade, 0.54975)

        # Alter the user's grade and proforma grade to ensure we trigger the update logic
        user0_entry = StudentGradebook.objects.get(user=self.users[0])
        user0_entry.grade = 0.25
        user0_entry.proforma_grade = 0.55
        user0_entry.save()

        # Run the command across all users, but just for the specified course
        generate_gradebook_entries.Command().handle(course_ids=course_ids)

        # Confirm that the gradebook has been properly updated
        current_entries = StudentGradebook.objects.all()
        self.assertEqual(len(current_entries), 3)
        current_entries = StudentGradebookHistory.objects.all()
        self.assertEqual(len(current_entries), 6)
        user0_entry = StudentGradebook.objects.get(user=self.users[0])
        self.assertEqual(user0_entry.grade, 0.50)
        self.assertEqual(user0_entry.proforma_grade, 0.54975)
        user1_entry = StudentGradebook.objects.get(user=self.users[1])
        self.assertEqual(user1_entry.grade, 0.48)
        self.assertEqual(user1_entry.proforma_grade, 0.5715)
        user2_entry = StudentGradebook.objects.get(user=self.users[2])
        self.assertEqual(user2_entry.grade, 0.72)
        self.assertEqual(user2_entry.proforma_grade, 0.85725)

        # Alter the user's progress and grade summaries to ensure we trigger the update logic
        user0_entry = StudentGradebook.objects.get(user=self.users[0])
        self.assertIn(json.dumps(self.problem_progress_summary), user0_entry.progress_summary)
        self.assertIn(json.dumps(self.problem_grade_summary), user0_entry.grade_summary)
        self.assertEqual(self.grading_policy, json.loads(user0_entry.grading_policy))
        user0_entry.progress_summary = ""
        user0_entry.grade_summary = ""
        user0_entry.grading_policy = ""
        user0_entry.save()

        # Run the command across all users, but just for the specified course
        generate_gradebook_entries.Command().handle(course_ids=course_ids)

        # Confirm that the gradebook has been properly updated
        current_entries = StudentGradebook.objects.all()
        self.assertEqual("", user0_entry.progress_summary)
        self.assertEqual("", user0_entry.grade_summary)
        self.assertEqual("", user0_entry.grading_policy)

        # Alter the user's empty progress and grade summaries to ensure we trigger the update logic
        user0_entry = StudentGradebook.objects.get(user=self.users[0])
        self.assertIn(json.dumps(self.problem_progress_summary), user0_entry.progress_summary)
        user0_entry.progress_summary = json.dumps({"progress": "summary"}, cls=EdxJSONEncoder)
        user0_entry.grade_summary = json.dumps({"grade": "summary"}, cls=EdxJSONEncoder)
        user0_entry.grading_policy = json.dumps({"grading": "policy"}, cls=EdxJSONEncoder)
        user0_entry.save()

        # Run the command across all users, but just for the specified course
        generate_gradebook_entries.Command().handle(course_ids=course_ids)

        # Confirm that the gradebook has been properly updated
        current_entries = StudentGradebook.objects.all()
        self.assertEqual(json.dumps({'progress': 'summary'}), user0_entry.progress_summary)
        self.assertEqual(json.dumps({"grade": "summary"}), user0_entry.grade_summary)
        self.assertEqual(json.dumps({'grading': "policy"}), user0_entry.grading_policy)
