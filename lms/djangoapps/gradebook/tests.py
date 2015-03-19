# pylint: disable=E1101
"""
Run these tests @ Devstack:
    paver test_system -s lms --test_id=lms/djangoapps/gradebook/tests.py
"""
from mock import MagicMock
import uuid

from django.test import TestCase
from django.test.utils import override_settings

from capa.tests.response_xml_factory import StringResponseXMLFactory
from courseware import module_render
from courseware.model_data import FieldDataCache
from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory

from gradebook.models import StudentGradebook, StudentGradebookHistory


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
@override_settings(STUDENT_GRADEBOOK=True)
class GradebookTests(TestCase):
    """ Test suite for Student Gradebook """

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
            course.id
        )._xmodule

    def setUp(self):
        self.test_server_prefix = 'https://testserver'
        self.user = UserFactory()
        self.score = 0.75

        self.course = CourseFactory.create()
        self.course.always_recalculate_grades = True
        test_data = '<html>{}</html>'.format(str(uuid.uuid4()))
        chapter1 = ItemFactory.create(
            category="chapter",
            parent_location=self.course.location,
            data=test_data,
            display_name="Chapter 1"
        )
        chapter2 = ItemFactory.create(
            category="chapter",
            parent_location=self.course.location,
            data=test_data,
            display_name="Chapter 2"
        )
        ItemFactory.create(
            category="sequential",
            parent_location=chapter1.location,
            data=test_data,
            display_name="Sequence 1",
        )
        ItemFactory.create(
            category="sequential",
            parent_location=chapter2.location,
            data=test_data,
            display_name="Sequence 2",
        )
        ItemFactory.create(
            parent_location=chapter2.location,
            category='problem',
            data=StringResponseXMLFactory().build_xml(answer='foo'),
            metadata={'rerandomize': 'always'},
            display_name="test problem 1",
            max_grade=45
        )
        self.problem = ItemFactory.create(
            parent_location=chapter1.location,
            category='problem',
            data=StringResponseXMLFactory().build_xml(answer='bar'),
            display_name="homework problem 1",
            metadata={'rerandomize': 'always', 'graded': True, 'format': "Homework"}
        )
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

    def test_receiver_on_score_changed(self):
        module = self.get_module_for_user(self.user, self.course, self.problem)
        grade_dict = {'value': 0.75, 'max_value': 1, 'user_id': self.user.id}
        module.system.publish(module, 'grade', grade_dict)

        module = self.get_module_for_user(self.user, self.course, self.problem2)
        grade_dict = {'value': 0.95, 'max_value': 1, 'user_id': self.user.id}
        module.system.publish(module, 'grade', grade_dict)

        module = self.get_module_for_user(self.user, self.course, self.problem3)
        grade_dict = {'value': 0.86, 'max_value': 1, 'user_id': self.user.id}
        module.system.publish(module, 'grade', grade_dict)

        module = self.get_module_for_user(self.user, self.course, self.problem4)
        grade_dict = {'value': 0.92, 'max_value': 1, 'user_id': self.user.id}
        module.system.publish(module, 'grade', grade_dict)

        module = self.get_module_for_user(self.user, self.course, self.problem5)
        grade_dict = {'value': 0.87, 'max_value': 1, 'user_id': self.user.id}
        module.system.publish(module, 'grade', grade_dict)

        gradebook = StudentGradebook.objects.all()
        self.assertEqual(len(gradebook), 1)

        history = StudentGradebookHistory.objects.all()
        self.assertEqual(len(history), 5)
