"""
Test for student tasks.
"""

from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from student.models import CourseEnrollment
from student.scope_resolver import CourseEnrollmentsScopeResolver


class StudentTasksTestCase(ModuleStoreTestCase):
    """
    Tests of student.roles
    """

    def setUp(self):
        """
        setUp stuff
        """
        super(StudentTasksTestCase, self).setUp()
        self.course = CourseFactory.create()

    def test_resolve_course_enrollments(self):
        """
        Test that the CourseEnrollmentsScopeResolver actually returns all enrollments
        """

        test_user_1 = UserFactory.create(password='test_pass')
        CourseEnrollmentFactory(user=test_user_1, course_id=self.course.id)
        test_user_2 = UserFactory.create(password='test_pass')
        CourseEnrollmentFactory(user=test_user_2, course_id=self.course.id)
        test_user_3 = UserFactory.create(password='test_pass')
        enrollment = CourseEnrollmentFactory(user=test_user_3, course_id=self.course.id)

        # unenroll #3

        enrollment.is_active = False
        enrollment.save()

        resolver = CourseEnrollmentsScopeResolver()

        user_ids = resolver.resolve('course_enrollments', {'course_id': self.course.id}, None)

        # should have first two, but the third should not be present

        self.assertTrue(test_user_1.id in user_ids)
        self.assertTrue(test_user_2.id in user_ids)

        self.assertFalse(test_user_3.id in user_ids)

    def test_bad_params(self):
        """
        Makes sure the resolver returns None if all parameters aren't passed
        """

        resolver = CourseEnrollmentsScopeResolver()

        self.assertIsNone(resolver.resolve('bad', {'course_id': 'foo'}, None))
        self.assertIsNone(resolver.resolve('course_enrollments', {'bad': 'foo'}, None))
