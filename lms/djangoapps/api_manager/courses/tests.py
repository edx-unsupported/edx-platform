# pylint: disable=E1103
"""
Run these tests @ Devstack:
    paver test_system -s lms --fasttest --fail_fast --verbose --test_id=lms/djangoapps/api_manager/courses
"""
from datetime import datetime, timedelta
import json
import uuid
import pytz
from django.utils import timezone
import mock
from random import randint
from urllib import urlencode
from freezegun import freeze_time
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client
from django.test.utils import override_settings

from capa.tests.response_xml_factory import StringResponseXMLFactory
from courseware import module_render
from courseware.tests.factories import StudentModuleFactory
from courseware.model_data import FieldDataCache
from django_comment_common.models import Role, FORUM_ROLE_MODERATOR
from gradebook.models import StudentGradebook
from instructor.access import allow_access
from edxsolutions.organizations.models import Organization
from projects.models import Workgroup, Project
from student.tests.factories import UserFactory, CourseEnrollmentFactory, GroupFactory
from student.models import CourseEnrollment
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase, mixed_store_config
from xmodule.modulestore import ModuleStoreEnum
from api_manager.courseware_access import get_course_key
from api_manager.models import GroupProfile

from .content import TEST_COURSE_OVERVIEW_CONTENT, TEST_COURSE_UPDATES_CONTENT, TEST_COURSE_UPDATES_CONTENT_LEGACY
from .content import TEST_STATIC_TAB1_CONTENT, TEST_STATIC_TAB2_CONTENT


MODULESTORE_CONFIG = mixed_store_config(settings.COMMON_TEST_DATA_ROOT, {}, include_xml=False)
TEST_API_KEY = str(uuid.uuid4())
USER_COUNT = 6
SAMPLE_GRADE_DATA_COUNT = 4


class SecureClient(Client):
    """ Django test client using a "secure" connection. """
    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({'SERVER_PORT': 443, 'wsgi.url_scheme': 'https'})
        super(SecureClient, self).__init__(*args, **kwargs)


def _fake_get_course_social_stats(course_id, end_date=None):
    if end_date:
        raise Exception("Expected None for end_date parameter")

    course_key = get_course_key(course_id)
    users = CourseEnrollment.objects.users_enrolled_in(course_key)
    return {str(user.id): {user.first_name: user.last_name} for user in users}


def _fake_get_course_social_stats_date_expected(course_id, end_date=None):
    if not end_date:
        raise Exception("Expected non-None end_date parameter")
    return {
        '2': {'two': 'two-two'},
        '3': {'three': 'three-three-three'}
    }


def _fake_get_course_thread_stats(course_id):
    return {
        'num_threads': 5,
        'num_active_threads': 3
    }


@mock.patch("api_manager.courses.views.get_course_thread_stats", _fake_get_course_thread_stats)
@override_settings(MODULESTORE=MODULESTORE_CONFIG)
@override_settings(EDX_API_KEY=TEST_API_KEY)
@mock.patch.dict("django.conf.settings.FEATURES",
                 {'ENFORCE_PASSWORD_POLICY': False, 'ADVANCED_SECURITY': False, 'PREVENT_CONCURRENT_LOGINS': False})
class CoursesApiTests(ModuleStoreTestCase):
    """ Test suite for Courses API views """

    def get_module_for_user(self, user, course, problem):
        """Helper function to get useful module at self.location in self.course_id for user"""
        mock_request = mock.MagicMock()
        mock_request.user = user
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            course.id, user, course, depth=2)
        module = module_render.get_module(  # pylint: disable=protected-access
            user,
            mock_request,
            problem.location,
            field_data_cache,
        )
        return module

    def setUp(self):
        super(CoursesApiTests, self).setUp()
        self.test_server_prefix = 'https://testserver'
        self.base_courses_uri = '/api/server/courses'
        self.base_groups_uri = '/api/server/groups'
        self.base_users_uri = '/api/server/users'
        self.base_organizations_uri = '/api/server/organizations/'
        self.base_projects_uri = '/api/server/projects/'
        self.base_workgroups_uri = '/api/server/workgroups/'
        self.test_group_name = 'Alpha Group'
        self.attempts = 3

        self.course_start_date = timezone.now() + relativedelta(days=-1)
        self.course_end_date = timezone.now() + relativedelta(days=60)
        self.course = CourseFactory.create(
            start=self.course_start_date,
            end=self.course_end_date,
        )
        self.test_data = '<html>{}</html>'.format(str(uuid.uuid4()))

        self.chapter = ItemFactory.create(
            category="chapter",
            parent_location=self.course.location,
            data=self.test_data,
            due=self.course_end_date,
            display_name="Overview",
        )

        self.course_project = ItemFactory.create(
            category="chapter",
            parent_location=self.course.location,
            data=self.test_data,
            display_name="Group Project"
        )

        self.course_project2 = ItemFactory.create(
            category="chapter",
            parent_location=self.course.location,
            data=self.test_data,
            display_name="Group Project2"
        )

        self.course_content2 = ItemFactory.create(
            category="sequential",
            parent_location=self.chapter.location,
            data=self.test_data,
            display_name="Sequential",
        )

        self.content_child2 = ItemFactory.create(
            category="vertical",
            parent_location=self.course_content2.location,
            data=self.test_data,
            display_name="Vertical Sequence"
        )

        self.course_content = ItemFactory.create(
            category="videosequence",
            parent_location=self.content_child2.location,
            data=self.test_data,
            display_name="Video_Sequence",
        )

        self.content_child = ItemFactory.create(
            category="video",
            parent_location=self.course_content.location,
            data=self.test_data,
            display_name="Video"
        )

        self.content_subchild = ItemFactory.create(
            category="video",
            parent_location=self.content_child2.location,
            data=self.test_data,
            display_name="Child Video",
        )

        self.overview = ItemFactory.create(
            category="about",
            parent_location=self.course.location,
            data=TEST_COURSE_OVERVIEW_CONTENT,
            display_name="overview"
        )

        self.updates = ItemFactory.create(
            category="course_info",
            parent_location=self.course.location,
            data=TEST_COURSE_UPDATES_CONTENT,
            display_name="updates"
        )

        self.static_tab1 = ItemFactory.create(
            category="static_tab",
            parent_location=self.course.location,
            data=TEST_STATIC_TAB1_CONTENT,
            display_name="syllabus",
            name="Static+Tab"
        )

        self.static_tab2 = ItemFactory.create(
            category="static_tab",
            parent_location=self.course.location,
            data=TEST_STATIC_TAB2_CONTENT,
            display_name="readings"
        )

        self.sub_section = ItemFactory.create(
            parent_location=self.chapter.location,
            category="sequential",
            display_name=u"test subsection",
        )

        self.unit = ItemFactory.create(
            parent_location=self.sub_section.location,
            category="vertical",
            metadata={'graded': True, 'format': 'Homework'},
            display_name=u"test unit",
        )

        self.dash_unit = ItemFactory.create(
            parent_location=self.sub_section.location,
            category="vertical-with-dash",
            metadata={'graded': True, 'format': 'Homework'},
            display_name=u"test unit 2",
        )

        self.empty_course = CourseFactory.create(
            start=self.course_start_date,
            end=self.course_end_date,
            org="MTD"
        )

        self.users = [UserFactory.create(username="testuser" + str(__), profile='test') for __ in xrange(USER_COUNT)]

        for user in self.users:
            CourseEnrollmentFactory.create(user=user, course_id=self.course.id)
            user_profile = user.profile
            user_profile.avatar_url = 'http://example.com/{}.png'.format(user.id)
            user_profile.title = 'Software Engineer {}'.format(user.id)
            user_profile.city = 'Cambridge'
            user_profile.save()

        for i in xrange(SAMPLE_GRADE_DATA_COUNT - 1):
            section = 'Midterm Exam'
            if i % 2 is 0:
                section = "Final Exam"
            self.item = ItemFactory.create(
                parent_location=self.chapter.location,
                category='problem',
                data=StringResponseXMLFactory().build_xml(answer='bar'),
                display_name='Problem {}'.format(i),
                metadata={'rerandomize': 'always', 'graded': True, 'format': section}
            )

            for j, user in enumerate(self.users):
                points_scored = (j + 1) * 20
                points_possible = 100
                module = self.get_module_for_user(user, self.course, self.item)
                grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user.id}
                module.system.publish(module, 'grade', grade_dict)

                StudentModuleFactory.create(
                    course_id=self.course.id,
                    module_type='sequential',
                    module_state_key=self.item.location,
                )

        self.test_course_id = unicode(self.course.id)
        self.test_bogus_course_id = 'foo/bar/baz'
        self.test_course_name = self.course.display_name
        self.test_course_number = self.course.number
        self.test_course_org = self.course.org
        self.test_chapter_id = unicode(self.chapter.scope_ids.usage_id)
        self.test_course_content_id = unicode(self.course_content.scope_ids.usage_id)
        self.test_bogus_content_id = "j5y://foo/bar/baz"
        self.test_content_child_id = unicode(self.content_child.scope_ids.usage_id)
        self.base_course_content_uri = '{}/{}/content'.format(self.base_courses_uri, self.test_course_id)
        self.base_chapters_uri = self.base_course_content_uri + '?type=chapter'

        self.client = SecureClient()
        cache.clear()

        Role.objects.get_or_create(
            name=FORUM_ROLE_MODERATOR,
            course_id=self.course.id)

    def do_get(self, uri):
        """Submit an HTTP GET request"""
        headers = {
            'Content-Type': 'application/json',
            'X-Edx-Api-Key': str(TEST_API_KEY),
        }
        response = self.client.get(uri, headers=headers)
        return response

    def do_post(self, uri, data):
        """Submit an HTTP POST request"""
        headers = {
            'X-Edx-Api-Key': str(TEST_API_KEY),
            'Content-Type': 'application/json'
        }
        json_data = json.dumps(data)
        response = self.client.post(uri, headers=headers, content_type='application/json', data=json_data)
        return response

    def do_delete(self, uri):
        """Submit an HTTP DELETE request"""
        headers = {
            'Content-Type': 'application/json',
            'X-Edx-Api-Key': str(TEST_API_KEY),
        }
        response = self.client.delete(uri, headers=headers)
        return response

    def _find_item_by_class(self, items, class_name):
        """Helper method to match a single matching item"""
        for item in items:
            if item['class'] == class_name:
                return item
        return None

    def _setup_courses_metrics_grades_leaders(self):
        """Setup for courses metrics grades leaders"""
        course = CourseFactory.create(
            number='3035',
            name='metrics_grades_leaders',
            start=self.course_start_date,
            end=self.course_end_date
        )

        chapter = ItemFactory.create(
            category="chapter",
            parent_location=course.location,
            data=self.test_data,
            due=self.course_end_date,
            display_name=u"3035 Overview"
        )

        # Create the set of users that will enroll in these courses
        users = [UserFactory.create(username="testleaderuser" + str(__), profile='test') for __ in xrange(USER_COUNT)]
        groups = GroupFactory.create_batch(2)
        for i, user in enumerate(users):
            user.groups.add(groups[i % 2])
            CourseEnrollmentFactory.create(user=user, course_id=course.id)

        users[0].groups.add(groups[1])

        for i in xrange(SAMPLE_GRADE_DATA_COUNT - 1):
            section = 'Midterm Exam'
            if i % 2 is 0:
                section = "Final Exam"
            item = ItemFactory.create(
                parent_location=chapter.location,
                category='problem',
                data=StringResponseXMLFactory().build_xml(answer='bar'),
                display_name='Problem {}'.format(i),
                metadata={'rerandomize': 'always', 'graded': True, 'format': section}
            )

            for j, user in enumerate(users):
                points_scored = (j + 1) * 20
                points_possible = 100
                module = self.get_module_for_user(user, course, item)
                grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user.id}
                module.system.publish(module, 'grade', grade_dict)

        # make the last user an observer to assert that its content is being filtered out from
        # the aggregates
        allow_access(course, users[USER_COUNT - 1], 'observer')

        item = ItemFactory.create(
            parent_location=chapter.location,
            category='mentoring',
            data=StringResponseXMLFactory().build_xml(answer='foo'),
            display_name=u"test problem same points",
            metadata={'rerandomize': 'always', 'graded': True, 'format': "Midterm Exam"}
        )

        points_scored = 2.25
        points_possible = 4
        user = users[USER_COUNT - 3]
        module = self.get_module_for_user(user, course, item)
        grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user.id}
        module.system.publish(module, 'grade', grade_dict)

        points_scored = 2.25
        points_possible = 4
        user = users[USER_COUNT - 2]
        module = self.get_module_for_user(user, course, item)
        grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user.id}
        module.system.publish(module, 'grade', grade_dict)

        return {
            'course': course,
            'chapter': chapter,
            'item': item,
            'users': users,
            'groups': groups
        }

    def _setup_courses_completions_leaders(self):
        """Setup for courses completions leaders"""
        course = CourseFactory.create(
            number='4033',
            name='leaders_by_completions',
            start=datetime(2014, 9, 16, 14, 30),
            end=datetime(2015, 1, 16)
        )

        chapter = ItemFactory.create(
            category="chapter",
            parent_location=course.location,
            data=self.test_data,
            due=datetime(2014, 5, 16, 14, 30),
            display_name="Overview"
        )

        sub_section = ItemFactory.create(
            parent_location=chapter.location,
            category="sequential",
            display_name=u"test subsection",
        )
        unit = ItemFactory.create(
            parent_location=sub_section.location,
            category="vertical",
            metadata={'graded': True, 'format': 'Homework'},
            display_name=u"test unit",
        )

        # create 5 users
        user_count = 5
        users = [UserFactory.create(username="testuser_cctest" + str(__), profile='test') for __ in xrange(user_count)]
        groups = GroupFactory.create_batch(2)

        for i, user in enumerate(users):
            user.groups.add(groups[i % 2])

        users[0].groups.add(groups[1])

        for user in users:
            CourseEnrollmentFactory.create(user=user, course_id=course.id)
            CourseEnrollmentFactory.create(user=user, course_id=self.course.id)

        test_course_id = unicode(course.id)
        completion_uri = '{}/{}/completions/'.format(self.base_courses_uri, test_course_id)
        leaders_uri = '{}/{}/metrics/completions/leaders/'.format(self.base_courses_uri, test_course_id)
        # Make last user as observer to make sure that data is being filtered out
        allow_access(course, users[user_count - 1], 'observer')

        contents = []
        for i in xrange(1, 26):
            local_content_name = 'Video_Sequence{}'.format(i)
            local_content = ItemFactory.create(
                category="videosequence",
                parent_location=unit.location,
                data=self.test_data,
                display_name=local_content_name
            )
            contents.append(local_content)
            if i < 3:
                user_id = users[0].id
            elif i < 10:
                user_id = users[1].id
            elif i < 17:
                user_id = users[2].id
            else:
                user_id = users[3].id

            content_id = unicode(local_content.scope_ids.usage_id)
            completions_data = {'content_id': content_id, 'user_id': user_id}
            response = self.do_post(completion_uri, completions_data)
            self.assertEqual(response.status_code, 201)

            # observer should complete everything, so we can assert that it is filtered out
            response = self.do_post(completion_uri, {
                'content_id': content_id, 'user_id': users[user_count - 1].id
            })
            self.assertEqual(response.status_code, 201)
        return {
            'leaders_uri': leaders_uri,
            'users': users,
            'contents': contents,
            'completion_uri': completion_uri,
            'groups': groups
        }

    def test_courses_list_get(self):
        test_uri = self.base_courses_uri
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)
        self.assertIsNotNone(response.data['count'])
        self.assertIsNotNone(response.data['num_pages'])
        matched_course = False
        for course in response.data['results']:
            if matched_course is False and course['id'] == self.test_course_id:
                self.assertEqual(course['name'], self.test_course_name)
                self.assertEqual(course['number'], self.test_course_number)
                self.assertEqual(course['org'], self.test_course_org)
                confirm_uri = self.test_server_prefix + test_uri + '/' + course['id']
                self.assertEqual(course['uri'], confirm_uri)
                matched_course = True
        self.assertTrue(matched_course)

    def test_courses_list_get_with_filter(self):
        test_uri = self.base_courses_uri
        courses = [self.test_course_id, unicode(self.empty_course.id)]
        params = {'course_id': ','.join(courses).encode('utf-8')}
        response = self.do_get('{}/?{}'.format(test_uri, urlencode(params)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['count'])
        self.assertIsNotNone(response.data['num_pages'])
        courses_in_result = []
        for course in response.data['results']:
            courses_in_result.append(course['id'])
            if course['id'] == self.test_course_id:
                self.assertEqual(course['name'], self.test_course_name)
                self.assertEqual(course['number'], self.test_course_number)
                self.assertEqual(course['org'], self.test_course_org)
                confirm_uri = self.test_server_prefix + test_uri + '/' + course['id']
                self.assertEqual(course['uri'], confirm_uri)
                self.assertIsNotNone(course['course_image_url'])
        self.assertItemsEqual(courses, courses_in_result)

    def test_course_detail_without_date_values(self):
        create_course_with_out_date_values = CourseFactory.create()  # pylint: disable=C0103
        test_uri = self.base_courses_uri + '/' + unicode(create_course_with_out_date_values.id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['start'], create_course_with_out_date_values.start)
        self.assertEqual(response.data['end'], create_course_with_out_date_values.end)

    def test_courses_detail_get(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], self.test_course_id)
        self.assertEqual(response.data['name'], self.test_course_name)
        self.assertEqual(datetime.strftime(response.data['start'], '%Y-%m-%d %H:%M:%S'), datetime.strftime(self.course.start, '%Y-%m-%d %H:%M:%S'))
        self.assertEqual(datetime.strftime(response.data['end'], '%Y-%m-%d %H:%M:%S'), datetime.strftime(self.course.end, '%Y-%m-%d %H:%M:%S'))
        self.assertEqual(response.data['number'], self.test_course_number)
        self.assertEqual(response.data['org'], self.test_course_org)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)

    def test_courses_detail_get_with_child_content(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id
        response = self.do_get('{}?depth=100'.format(test_uri))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], self.test_course_id)
        self.assertEqual(response.data['name'], self.test_course_name)
        self.assertEqual(response.data['number'], self.test_course_number)
        self.assertEqual(response.data['org'], self.test_course_org)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertGreater(len(response.data['content']), 0)
        for resource in response.data['resources']:
            response = self.do_get(resource['uri'])
            self.assertEqual(response.status_code, 200)

    def test_courses_detail_get_notfound(self):
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_tree_get(self):
        # query the course tree to quickly get naviation information
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '?depth=2'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['category'], 'course')
        self.assertEqual(response.data['name'], self.course.display_name)
        self.assertEqual(len(response.data['content']), 3)

        chapter = response.data['content'][0]
        self.assertEqual(chapter['category'], 'chapter')
        self.assertEqual(chapter['name'], 'Overview')
        # we should have 5 children of Overview chapter
        # 1 sequential, 1 vertical, 1 videosequence and 2 videos
        self.assertEqual(len(chapter['children']), 5)

        # Make sure one of the children should be a sequential
        sequential = [child for child in chapter['children'] if child['category'] == 'sequential']
        self.assertGreater(len(sequential), 0)

    def test_courses_tree_get_root(self):
        # query the course tree to quickly get naviation information
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '?depth=0'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['category'], 'course')
        self.assertEqual(response.data['name'], self.course.display_name)
        self.assertNotIn('content', response.data)

    def test_chapter_list_get(self):
        test_uri = self.base_chapters_uri
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        matched_chapter = False
        for chapter in response.data:
            if matched_chapter is False and chapter['id'] == self.test_chapter_id:
                self.assertIsNotNone(chapter['uri'])
                self.assertGreater(len(chapter['uri']), 0)
                confirm_uri = self.test_server_prefix + self.base_course_content_uri + '/' + chapter['id']
                self.assertEqual(chapter['uri'], confirm_uri)
                matched_chapter = True
        self.assertTrue(matched_chapter)

    def test_chapter_detail_get(self):
        test_uri = self.base_course_content_uri + '/' + self.test_chapter_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['id']), 0)
        self.assertEqual(response.data['id'], self.test_chapter_id)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertGreater(len(response.data['children']), 0)

    def test_course_content_list_get(self):
        test_uri = '{}/{}/children'.format(self.base_course_content_uri, self.test_course_content_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        matched_child = False
        for child in response.data:
            if matched_child is False and child['id'] == self.test_content_child_id:
                self.assertIsNotNone(child['uri'])
                self.assertGreater(len(child['uri']), 0)
                confirm_uri = self.test_server_prefix + self.base_course_content_uri + '/' + child['id']
                self.assertEqual(child['uri'], confirm_uri)
                matched_child = True
        self.assertTrue(matched_child)

    def test_course_content_list_get_invalid_course(self):
        test_uri = '{}/{}/content/{}/children'.format(self.base_courses_uri, self.test_bogus_course_id, unicode(self.course_project.scope_ids.usage_id))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_list_get_invalid_content(self):
        test_uri = '{}/{}/children'.format(self.base_course_content_uri, self.test_bogus_content_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_detail_get(self):
        test_uri = self.base_course_content_uri + '/' + self.test_course_content_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], self.test_course_content_id)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertGreater(len(response.data['children']), 0)

    def test_course_content_detail_get_with_extra_fields(self):
        test_uri = self.base_course_content_uri + '/' + self.test_course_content_id
        response = self.do_get('{}?include_fields=course_edit_method,edited_by'.format(test_uri))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertIsNotNone(response.data['course_edit_method'])
        self.assertEqual(response.data['edited_by'], ModuleStoreEnum.UserID.test)

    def test_course_content_detail_get_dashed_id(self):
        test_content_id = unicode(self.dash_unit.scope_ids.usage_id)
        test_uri = self.base_course_content_uri + '/' + test_content_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], test_content_id)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)

    def test_course_content_detail_get_course(self):
        test_uri = self.base_course_content_uri + '/' + self.test_course_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], self.test_course_id)
        confirm_uri = self.test_server_prefix + self.base_courses_uri + '/' + self.test_course_id
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertGreater(len(response.data['content']), 0)

    def test_course_content_detail_get_notfound(self):
        test_uri = self.base_course_content_uri + '/' + self.test_bogus_content_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_list_get_filtered_children_for_child(self):
        test_uri = self.base_course_content_uri + '/' + self.test_course_content_id + '/children?type=video'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        matched_child = False
        for child in response.data:
            if matched_child is False and child['id'] == self.test_content_child_id:
                confirm_uri = '{}{}/{}'.format(self.test_server_prefix, self.base_course_content_uri, child['id'])
                self.assertEqual(child['uri'], confirm_uri)
                matched_child = True
        self.assertTrue(matched_child)

    def test_course_content_list_get_notfound(self):
        test_uri = '{}{}/children?type=video'.format(self.base_course_content_uri, self.test_bogus_content_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_groups_list_post(self):
        data = {'name': self.test_group_name, 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']

        test_uri = '{}/{}/groups'.format(self.base_courses_uri, self.test_course_id)
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)

        confirm_uri = self.test_server_prefix + test_uri + '/' + str(group_id)
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertEqual(response.data['course_id'], str(self.test_course_id))
        self.assertEqual(response.data['group_id'], str(group_id))

    def test_courses_groups_list_get(self):
        test_uri = '{}/{}/groups'.format(self.base_courses_uri, self.test_course_id)
        course_fail_uri = '{}/{}/groups'.format(self.base_courses_uri, 'ed/Open_DemoX/edx_demo_course')
        for i in xrange(2):
            data_dict = {
                'name': 'Alpha Group {}'.format(i), 'type': 'Programming',
            }
            response = self.do_post(self.base_groups_uri, data_dict)
            group_id = response.data['id']
            data = {'group_id': group_id}
            self.assertEqual(response.status_code, 201)
            response = self.do_post(test_uri, data)
            self.assertEqual(response.status_code, 201)

        data_dict['type'] = 'Calculus'
        response = self.do_post(self.base_groups_uri, data_dict)
        group_id = response.data['id']
        data = {'group_id': group_id}
        self.assertEqual(response.status_code, 201)
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)

        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        courses_groups_uri = '{}?type={}'.format(test_uri, 'Programming')
        response = self.do_get(courses_groups_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        group_type_uri = '{}?type={}'.format(test_uri, 'Calculus')
        response = self.do_get(group_type_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        error_group_type_uri = '{}?type={}'.format(test_uri, 'error_type')
        response = self.do_get(error_group_type_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        response = self.do_get(course_fail_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_groups_list_post_duplicate(self):
        data = {'name': self.test_group_name, 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/groups'.format(self.base_courses_uri, self.test_course_id)
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 409)

    def test_courses_groups_list_post_invalid_course(self):
        test_uri = self.base_courses_uri + '/1239/87/8976/groups'
        data = {'group_id': "98723896"}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 404)

    def test_courses_groups_list_post_invalid_group(self):
        test_uri = '{}/{}/groups'.format(self.base_courses_uri, self.test_course_id)
        data = {'group_id': "98723896"}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 404)

    def test_courses_groups_detail_get(self):
        data = {'name': self.test_group_name, 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/groups'.format(self.base_courses_uri, self.test_course_id)
        data = {'group_id': response.data['id']}
        response = self.do_post(test_uri, data)
        test_uri = response.data['uri']
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertEqual(response.data['course_id'], self.test_course_id)
        self.assertEqual(response.data['group_id'], str(group_id))

    def test_courses_groups_detail_get_invalid_resources(self):
        test_uri = '{}/{}/groups/123145'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

        test_uri = '{}/{}/groups/123145'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

        data = {'name': self.test_group_name, 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        test_uri = '{}/{}/groups/{}'.format(self.base_courses_uri, self.test_course_id, response.data['id'])
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_groups_detail_delete(self):
        data = {'name': self.test_group_name, 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        test_uri = '{}/{}/groups'.format(self.base_courses_uri, self.test_course_id)
        data = {'group_id': response.data['id']}
        response = self.do_post(test_uri, data)
        test_uri = response.data['uri']
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)  # Idempotent
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_groups_detail_delete_invalid_course(self):
        test_uri = '{}/{}/groups/123124'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)

    def test_courses_groups_detail_delete_invalid_group(self):
        test_uri = '{}/{}/groups/123124'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)

    def test_courses_groups_detail_get_undefined(self):
        data = {'name': self.test_group_name, 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/groups/{}'.format(self.base_courses_uri, self.test_course_id, group_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_overview_get_unparsed(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/overview'

        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['overview_html'], self.overview.data)
        self.assertIn(self.course.course_image, response.data['course_image_url'])

    def test_courses_overview_get_parsed(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/overview?parse=true'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertIn(self.course.course_image, response.data['course_image_url'])
        sections = response.data['sections']
        self.assertEqual(len(sections), 5)
        self.assertIsNotNone(self._find_item_by_class(sections, 'about'))
        self.assertIsNotNone(self._find_item_by_class(sections, 'prerequisites'))
        self.assertIsNotNone(self._find_item_by_class(sections, 'course-staff'))
        self.assertIsNotNone(self._find_item_by_class(sections, 'faq'))
        self.assertIsNotNone(self._find_item_by_class(sections, 'intro-video'))

        course_staff = self._find_item_by_class(sections, 'course-staff')
        staff = course_staff['articles']
        self.assertEqual(len(staff), 3)
        self.assertEqual(staff[0]['class'], "teacher")
        self.assertEqual(staff[0]['name'], "Staff Member #1")
        self.assertEqual(staff[0]['image_src'], "/images/pl-faculty.png")
        self.assertIn("<p>Biography of instructor/staff member #1</p>", staff[0]['bio'])
        self.assertEqual(staff[1]['class'], "teacher")
        self.assertEqual(staff[1]['name'], "Staff Member #2")
        self.assertEqual(staff[1]['image_src'], "/images/pl-faculty.png")
        self.assertIn("<p>Biography of instructor/staff member #2</p>", staff[1]['bio'])
        self.assertEqual(staff[2]['class'], "author")
        body = staff[2]['body']
        self.assertGreater(len(body), 0)

        about = self._find_item_by_class(sections, 'about')
        self.assertGreater(len(about['body']), 0)
        prerequisites = self._find_item_by_class(sections, 'prerequisites')
        self.assertGreater(len(prerequisites['body']), 0)
        faq = self._find_item_by_class(sections, 'faq')
        self.assertGreater(len(faq['body']), 0)
        invalid_tab = self._find_item_by_class(sections, 'invalid_tab')
        self.assertFalse(invalid_tab)

        intro_video = self._find_item_by_class(sections, 'intro-video')
        self.assertEqual(len(intro_video['attributes']), 1)
        self.assertEqual(intro_video['attributes']['data-videoid'], 'foobar')

    def test_courses_overview_get_invalid_course(self):
        #try a bogus course_id to test failure case
        test_uri = '{}/{}/overview'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_overview_get_invalid_content(self):
        #try a bogus course_id to test failure case
        test_course = CourseFactory.create()
        test_uri = '{}/{}/overview'.format(self.base_courses_uri, unicode(test_course.id))
        ItemFactory.create(
            category="about",
            parent_location=test_course.location,
            data='',
            display_name="overview"
        )
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_updates_get(self):
        # first try raw without any parsing
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/updates'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['content'], self.updates.data)

        # then try parsed
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/updates?parse=True'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        postings = response.data['postings']
        self.assertEqual(len(postings), 4)
        self.assertEqual(postings[0]['date'], 'April 18, 2014')
        self.assertEqual(postings[0]['content'], 'This does not have a paragraph tag around it')
        self.assertEqual(postings[1]['date'], 'April 17, 2014')
        self.assertEqual(postings[1]['content'], 'Some text before paragraph tag<p>This is inside paragraph tag</p>Some text after tag')
        self.assertEqual(postings[2]['date'], 'April 16, 2014')
        self.assertEqual(postings[2]['content'], 'Some text before paragraph tag<p>This is inside paragraph tag</p>Some text after tag<p>one more</p>')
        self.assertEqual(postings[3]['date'], 'April 15, 2014')
        self.assertEqual(postings[3]['content'], '<p>A perfectly</p><p>formatted piece</p><p>of HTML</p>')

    def test_courses_updates_get_invalid_course(self):
        #try a bogus course_id to test failure case
        test_uri = '{}/{}/updates'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_updates_get_invalid_content(self):
        #try a bogus course_id to test failure case
        test_course = CourseFactory.create()
        ItemFactory.create(
            category="course_info",
            parent_location=test_course.location,
            data='',
            display_name="updates"
        )
        test_uri = '{}/{}/updates'.format(self.base_courses_uri, unicode(test_course.id))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_updates_legacy(self):
        #try a bogus course_id to test failure case
        test_course = CourseFactory.create()
        ItemFactory.create(
            category="course_info",
            parent_location=test_course.location,
            data=TEST_COURSE_UPDATES_CONTENT_LEGACY,
            display_name="updates"
        )
        test_uri = self.base_courses_uri + '/' + unicode(test_course.id) + '/updates'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['content'], TEST_COURSE_UPDATES_CONTENT_LEGACY)

        # then try parsed
        test_uri = self.base_courses_uri + '/' + unicode(test_course.id) + '/updates?parse=True'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        postings = response.data['postings']
        self.assertEqual(len(postings), 4)
        self.assertEqual(postings[0]['date'], 'April 18, 2014')
        self.assertEqual(postings[0]['content'], 'This is some legacy content')
        self.assertEqual(postings[1]['date'], 'April 17, 2014')
        self.assertEqual(postings[1]['content'], 'Some text before paragraph tag<p>This is inside paragraph tag</p>Some text after tag')
        self.assertEqual(postings[2]['date'], 'April 16, 2014')
        self.assertEqual(postings[2]['content'], 'Some text before paragraph tag<p>This is inside paragraph tag</p>Some text after tag<p>one more</p>')
        self.assertEqual(postings[3]['date'], 'April 15, 2014')
        self.assertEqual(postings[3]['content'], '<p>A perfectly</p><p>formatted piece</p><p>of HTML</p>')

    def test_static_tab_list_get(self):
        test_uri = '{}/{}/static_tabs'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        tabs = response.data['tabs']
        self.assertEqual(len(tabs), 2)
        self.assertEqual(tabs[0]['id'], u'syllabus')
        self.assertEqual(tabs[1]['id'], u'readings')

        # now try when we get the details on the tabs
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs?detail=true'
        response = self.do_get(test_uri)

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        tabs = response.data['tabs']
        self.assertEqual(tabs[0]['id'], u'syllabus')
        self.assertEqual(tabs[0]['content'], self.static_tab1.data)
        self.assertEqual(tabs[1]['id'], u'readings')
        self.assertEqual(tabs[1]['content'], self.static_tab2.data)

        # get syllabus tab contents from cache
        cache_key = u'course.{course_id}.static.tab.{url_slug}.contents'.format(
            course_id=self.test_course_id,
            url_slug=tabs[0]['id']
        )
        tab1_content = cache.get(cache_key)
        self.assertTrue(tab1_content is not None)
        self.assertEqual(tab1_content, self.static_tab1.data)

        # get readings tab contents from cache
        cache_key = u'course.{course_id}.static.tab.{url_slug}.contents'.format(
            course_id=self.test_course_id,
            url_slug=tabs[1]['id']
        )
        tab2_content = cache.get(cache_key)
        self.assertTrue(tab2_content is not None)
        self.assertEqual(tab2_content, self.static_tab2.data)

    def test_static_tab_list_get_invalid_course(self):
        #try a bogus course_id to test failure case
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id + '/static_tabs'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_static_tab_detail_get_by_name(self):
        # get course static tab by tab name
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs/Static+Tab'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        tab = response.data
        self.assertEqual(tab['id'], u'syllabus')
        self.assertEqual(tab['name'], u'Static+Tab')
        self.assertEqual(tab['content'], self.static_tab1.data)

        # now try to get syllabus tab contents from cache
        cache_key = u'course.{course_id}.static.tab.{url_slug}.contents'.format(
            course_id=self.test_course_id,
            url_slug=tab['id']
        )
        tab_contents = cache.get(cache_key)
        self.assertTrue(tab_contents is not None)
        self.assertEqual(tab_contents, self.static_tab1.data)

    def test_static_tab_detail_get_by_url_slug(self):
        # get course static tab by url_slug
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs/readings'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        tab = response.data
        self.assertEqual(tab['id'], u'readings')
        self.assertEqual(tab['content'], self.static_tab2.data)

        # now try to get readings tab contents from cache
        cache_key = u'course.{course_id}.static.tab.{url_slug}.contents'.format(
            course_id=self.test_course_id,
            url_slug=tab['id']
        )
        tab_contents = cache.get(cache_key)
        self.assertTrue(tab_contents is not None)
        self.assertEqual(tab_contents, self.static_tab2.data)

    @override_settings(STATIC_TAB_CONTENTS_CACHE_MAX_SIZE_LIMIT=200)
    def test_static_tab_content_cache_max_size_limit(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs/syllabus'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        tab = response.data
        self.assertEqual(tab['id'], u'syllabus')
        self.assertEqual(tab['content'], self.static_tab1.data)

        # try to get syllabus tab contents from cache
        cache_key = u'course.{course_id}.static.tab.{url_slug}.contents'.format(
            course_id=self.test_course_id,
            url_slug=tab['id']
        )
        tab_contents = cache.get(cache_key)
        self.assertTrue(tab_contents is not None)
        self.assertEqual(tab_contents, self.static_tab1.data)

        # now test static tab with content size greater than 200 bytes
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs/readings'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        tab = response.data
        self.assertEqual(tab['id'], u'readings')
        self.assertEqual(tab['content'], self.static_tab2.data)

        # try to get readings tab contents from cache
        cache_key = u'course.{course_id}.static.tab.{url_slug}.contents'.format(
            course_id=self.test_course_id,
            url_slug=tab['id']
        )
        tab_contents = cache.get(cache_key)
        self.assertTrue(tab_contents is None)

    @override_settings(STATIC_TAB_CONTENTS_CACHE_TTL=60)
    def test_static_tab_content_cache_time_to_live(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs/syllabus'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        tab = response.data
        self.assertEqual(tab['id'], u'syllabus')
        self.assertEqual(tab['content'], self.static_tab1.data)

        cache_key = u'course.{course_id}.static.tab.{url_slug}.contents'.format(
            course_id=self.test_course_id,
            url_slug=tab['id']
        )

        # try to get syllabus tab contents from cache
        tab_contents = cache.get(cache_key)
        self.assertTrue(tab_contents is not None)
        self.assertEqual(tab_contents, self.static_tab1.data)

        # now reset the time to 1 minute and 5 seconds from now in future to expire cache
        reset_time = datetime.now(pytz.UTC) + timedelta(seconds=65)
        with freeze_time(reset_time):
            # try to get syllabus tab contents from cache again
            tab_contents = cache.get(cache_key)
            self.assertTrue(tab_contents is None)

    def test_static_tab_detail_get_invalid_course(self):
        # try a bogus courseId
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id + '/static_tabs/syllabus'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_static_tab_detail_get_invalid_item(self):
        # try a not found item
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs/bogus'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_users_list_get_no_students(self):
        course = CourseFactory.create(display_name="TEST COURSE", org='TESTORG')
        test_uri = self.base_courses_uri + '/' + unicode(course.id) + '/users'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        # assert that there is no enrolled students
        enrollments = response.data['enrollments']
        self.assertEqual(len(enrollments), 0)
        self.assertNotIn('pending_enrollments', response.data)

    def test_courses_users_list_invalid_course(self):
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id + '/users'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_users_list_post_nonexisting_user_deny(self):
        # enroll a non-existing student
        # first, don't allow non-existing
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        post_data = {
            'email': 'test+pending@tester.com',
            'allow_pending': False,
        }
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 400)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_courses_users_list_post_nonexisting_user_allow(self):
        course = CourseFactory.create(display_name="TEST COURSE", org='TESTORG2')
        test_uri = self.base_courses_uri + '/' + unicode(course.id) + '/users'
        post_data = {}
        post_data['email'] = 'test+pending@tester.com'
        post_data['allow_pending'] = True
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 201)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['enrollments']), 0)

    def test_courses_users_list_post_existing_user(self):
        # create a new user (note, this calls into the /users/ subsystem)
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        test_user_uri = self.base_users_uri
        local_username = "some_test_user" + str(randint(11, 99))
        local_email = "test+notpending@tester.com"
        data = {
            'email': local_email,
            'username': local_username,
            'password': 'fooabr',
            'first_name': 'Joe',
            'last_name': 'Brown'
        }
        response = self.do_post(test_user_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(response.data['id'], 0)
        created_user_id = response.data['id']

        # now enroll this user in the course
        post_data = {}
        post_data['user_id'] = created_user_id
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 201)

    def test_courses_users_list_post_invalid_course(self):
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id + '/users'
        post_data = {}
        post_data['email'] = 'test+pending@tester.com'
        post_data['allow_pending'] = True
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 404)

    def test_courses_users_list_post_invalid_user(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        post_data = {}
        post_data['user_id'] = '123123124'
        post_data['allow_pending'] = True
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 404)

    def test_courses_users_list_post_invalid_payload(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        post_data = {}
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 400)

    def test_courses_users_list_get(self):
        # create a new user (note, this calls into the /users/ subsystem)
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        test_user_uri = self.base_users_uri
        local_username = "some_test_user" + str(randint(11, 99))
        local_email = "test+notpending@tester.com"
        data = {
            'email': local_email,
            'username': local_username,
            'password': 'fooabr',
            'first_name': 'Joe',
            'last_name': 'Brown'
        }
        response = self.do_post(test_user_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(response.data['id'], 0)
        created_user_id = response.data['id']
        post_data = {}
        post_data['user_id'] = created_user_id
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 201)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)

    def test_courses_users_list_get_attributes(self):
        """ Test presence of newly added attributes to courses users list api """
        course = CourseFactory.create(
            number='3035',
            name='metrics_grades_leaders',
            start=self.course_start_date,
            end=self.course_end_date
        )
        test_uri = self.base_courses_uri + '/' + unicode(course.id) + '/users'
        user = UserFactory.create(username="testuserattributes", profile='test')
        CourseEnrollmentFactory.create(user=user, course_id=course.id)

        data = {
            'name': 'Test Organization Attributes',
            'display_name': 'Test Org Display Name Attributes',
            'users': [user.id]
        }
        response = self.do_post(self.base_organizations_uri, data)
        self.assertEqual(response.status_code, 201)

        group = GroupFactory.create()
        GroupProfile.objects.create(group=group, name='role1', group_type='permission')
        user.groups.add(group)

        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data['enrollments'][0])
        self.assertIn('email', response.data['enrollments'][0])
        self.assertIn('username', response.data['enrollments'][0])
        self.assertIn('last_login', response.data['enrollments'][0])
        self.assertIn('full_name', response.data['enrollments'][0])
        self.assertIn('is_active', response.data['enrollments'][0])
        self.assertIsNotNone(response.data['enrollments'][0]['organizations'])
        self.assertIn('url', response.data['enrollments'][0]['organizations'][0])
        self.assertIn('id', response.data['enrollments'][0]['organizations'][0])
        self.assertIn('name', response.data['enrollments'][0]['organizations'][0])
        self.assertIn('created', response.data['enrollments'][0]['organizations'][0])
        self.assertIn('display_name', response.data['enrollments'][0]['organizations'][0])
        self.assertIn('logo_url', response.data['enrollments'][0]['organizations'][0])
        self.assertIsNotNone(response.data['enrollments'][0]['roles'])
        self.assertIn('id', response.data['enrollments'][0]['roles'][0])
        self.assertIn('name', response.data['enrollments'][0]['roles'][0])

    def test_courses_users_list_get_filter_by_orgs(self):
        # create 5 users
        users = []
        for i in xrange(1, 6):
            data = {
                'email': 'test{}@example.com'.format(i),
                'username': 'test_user{}'.format(i),
                'password': 'test_pass',
                'first_name': 'John{}'.format(i),
                'last_name': 'Doe{}'.format(i)
            }
            response = self.do_post(self.base_users_uri, data)
            self.assertEqual(response.status_code, 201)
            users.append(response.data['id'])

        # create 3 organizations each one having one user
        org_ids = []
        for i in xrange(1, 4):
            data = {
                'name': '{} {}'.format('Test Organization', i),
                'display_name': '{} {}'.format('Test Org Display Name', i),
                'users': [users[i]]
            }
            response = self.do_post(self.base_organizations_uri, data)
            self.assertEqual(response.status_code, 201)
            self.assertGreater(response.data['id'], 0)
            org_ids.append(response.data['id'])

        # enroll all users in course
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        for user in users:
            data = {'user_id': user}
            response = self.do_post(test_uri, data)
            self.assertEqual(response.status_code, 201)

        # retrieve all users enrolled in the course
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['enrollments']), 5)

        # retrieve users by organization
        response = self.do_get('{}?organizations={}'.format(test_uri, org_ids[0]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['enrollments']), 1)

        # retrieve all users enrolled in the course
        response = self.do_get('{}?organizations={},{},{}'.format(test_uri, org_ids[0], org_ids[1], org_ids[2]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['enrollments']), 3)

    def test_courses_users_list_get_filter_by_groups(self):
        # create 2 groups
        group_ids = []
        for i in xrange(1, 3):
            data = {'name': '{} {}'.format(self.test_group_name, i), 'type': 'test'}
            response = self.do_post(self.base_groups_uri, data)
            self.assertEqual(response.status_code, 201)
            group_ids.append(response.data['id'])

        # create 5 users
        users = []
        for i in xrange(0, 5):
            data = {
                'email': 'test{}@example.com'.format(i),
                'username': 'test_user{}'.format(i),
                'password': 'test_pass',
                'first_name': 'John{}'.format(i),
                'last_name': 'Doe{}'.format(i)
            }
            response = self.do_post(self.base_users_uri, data)
            self.assertEqual(response.status_code, 201)
            users.append(response.data['id'])
            if i < 2:
                data = {'user_id': response.data['id']}
                response = self.do_post('{}{}/users'.format(self.base_groups_uri, group_ids[i]), data)
                self.assertEqual(response.status_code, 201)

        # enroll all users in course
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        for user in users:
            data = {'user_id': user}
            response = self.do_post(test_uri, data)
            self.assertEqual(response.status_code, 201)

        # retrieve all users enrolled in the course and member of group 1
        response = self.do_get('{}?groups={}'.format(test_uri, group_ids[0]))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['enrollments']), 1)

        # retrieve all users enrolled in the course and member of group 1 and group 2
        response = self.do_get('{}?groups={},{}'.format(test_uri, group_ids[0], group_ids[1]))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['enrollments']), 2)

        # retrieve all users enrolled in the course and not member of group 1
        response = self.do_get('{}?exclude_groups={}'.format(test_uri, group_ids[0]))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['enrollments']), 4)

    def test_courses_users_list_get_filter_by_workgroups(self):
        """ Test courses users list workgroup filter """
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        organization = Organization.objects.create(
            name="Test Organization",
            display_name='Test Org Display Name',
        )
        project = Project.objects.create(course_id=self.test_course_id,
                                         content_id=self.test_course_content_id,
                                         organization=organization)
        # create 2 work groups
        workgroups = []
        workgroups.append(Workgroup.objects.create(name="Group1", project_id=project.id))
        workgroups.append(Workgroup.objects.create(name="Group2", project_id=project.id))
        workgroup_ids = ','.join([str(workgroup.id) for workgroup in workgroups])

        # create 5 users
        users = UserFactory.create_batch(5)

        for i, user in enumerate(users):
            workgroups[i % 2].add_user(user)

        # enroll all users in course
        for user in users:
            CourseEnrollmentFactory.create(user=user, course_id=self.test_course_id)

        # retrieve all users enrolled in the course and member of workgroup 1
        response = self.do_get('{}?workgroups={}'.format(test_uri, workgroups[0].id))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['enrollments']), 3)

        # retrieve all users enrolled in the course and member of workgroup 1 and workgroup 2
        response = self.do_get('{}?workgroups={}'.format(test_uri, workgroup_ids))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['enrollments']), 5)

    def test_courses_users_detail_get(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        test_user_uri = self.base_users_uri
        local_username = "some_test_user" + str(randint(11, 99))
        local_email = "test+notpending@tester.com"
        data = {
            'email': local_email,
            'username': local_username,
            'password': 'fooabr',
            'first_name': 'Joe',
            'last_name': 'Brown'
        }
        response = self.do_post(test_user_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(response.data['id'], 0)
        created_user_id = response.data['id']

        # Submit the query when unenrolled
        confirm_uri = '{}/{}'.format(test_uri, created_user_id)
        response = self.do_get(confirm_uri)
        self.assertEqual(response.status_code, 404)

        # now enroll this user in the course
        post_data = {}
        post_data['user_id'] = created_user_id
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 201)
        confirm_uri = '{}/{}'.format(test_uri, created_user_id)
        response = self.do_get(confirm_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_courses_users_detail_get_invalid_course(self):
        test_uri = '{}/{}/users/{}'.format(self.base_courses_uri, self.test_bogus_course_id, self.users[0].id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)
        self.assertGreater(len(response.data), 0)

    def test_courses_users_detail_get_invalid_user(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users/213432'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)
        self.assertGreater(len(response.data), 0)

    def test_courses_users_detail_delete(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        test_user_uri = self.base_users_uri
        local_username = "some_test_user" + str(randint(11, 99))
        local_email = "test+notpending@tester.com"
        data = {
            'email': local_email,
            'username': local_username,
            'password': 'fooabr',
            'first_name': 'Joe',
            'last_name': 'Brown'
        }
        response = self.do_post(test_user_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(response.data['id'], 0)
        created_user_id = response.data['id']

        # now enroll this user in the course
        post_data = {}
        post_data['user_id'] = created_user_id
        response = self.do_post(test_uri, post_data)
        self.assertEqual(response.status_code, 201)
        confirm_uri = '{}/{}'.format(test_uri, created_user_id)
        response = self.do_get(confirm_uri)
        self.assertEqual(response.status_code, 200)
        response = self.do_delete(confirm_uri)
        self.assertEqual(response.status_code, 204)

    def test_courses_users_detail_delete_invalid_course(self):
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id + '/users/1'
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_users_detail_delete_invalid_user(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users/213432'
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)

    def test_course_content_groups_list_post(self):
        data = {'name': 'Alpha Group', 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        data = {'name': 'Beta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/groups'.format(self.base_course_content_uri, unicode(self.course_project.scope_ids.usage_id))
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        confirm_uri = self.test_server_prefix + test_uri + '/' + str(group_id)
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertEqual(response.data['course_id'], str(self.test_course_id))
        self.assertEqual(response.data['content_id'], unicode(self.course_project.scope_ids.usage_id))
        self.assertEqual(response.data['group_id'], str(group_id))

    def test_course_content_groups_list_post_duplicate(self):
        data = {'name': 'Beta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/groups'.format(self.base_course_content_uri, unicode(self.course_project.scope_ids.usage_id))
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 409)

    def test_course_content_groups_list_post_invalid_course(self):
        data = {'name': 'Beta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/content/{}/groups'.format(
            self.base_courses_uri,
            self.test_bogus_course_id,
            unicode(self.course_project.scope_ids.usage_id)
        )
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_list_post_invalid_content(self):
        data = {'name': 'Beta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/content/{}/groups'.format(
            self.base_courses_uri,
            self.test_course_id,
            self.test_bogus_content_id
        )
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_list_post_invalid_group(self):
        test_uri = '{}/{}/content/{}/groups'.format(
            self.base_courses_uri,
            self.test_course_id,
            unicode(self.course_project.scope_ids.usage_id)
        )
        data = {'group_id': '12398721'}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_list_post_missing_group(self):
        test_uri = '{}/{}/content/{}/groups'.format(
            self.base_courses_uri,
            self.test_course_id,
            unicode(self.course_project.scope_ids.usage_id)
        )
        response = self.do_post(test_uri, {})
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_list_get(self):
        test_uri = '{}/{}/groups'.format(self.base_course_content_uri, unicode(self.course_project.scope_ids.usage_id))
        data = {'name': 'Alpha Group', 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        alpha_group_id = response.data['id']
        data = {'group_id': alpha_group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)

        # Add a profile-less group to the system to offset the identifiers
        Group.objects.create(name='Offset Group')

        data = {'name': 'Beta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)

        data = {'name': 'Delta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)

        data = {'name': 'Gamma Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)
        gamma_group_id = response.data['id']
        data = {'group_id': gamma_group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)

        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['group_id'], alpha_group_id)
        self.assertEqual(response.data[1]['group_id'], gamma_group_id)

        test_uri = test_uri + '?type=project'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_course_content_groups_list_get_invalid_course(self):
        test_uri = '{}/{}/content/{}/groups'.format(
            self.base_courses_uri,
            self.test_bogus_course_id,
            unicode(self.course_project.scope_ids.usage_id)
        )
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_list_get_invalid_content(self):
        test_uri = '{}/{}/content/{}/groups'.format(
            self.base_courses_uri,
            self.test_course_id,
            self.test_bogus_content_id
        )
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_list_get_filter_by_type(self):
        data = {'name': 'Alpha Group', 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        data = {'name': 'Beta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)
        self.assertEqual(response.status_code, 201)
        group_id = response.data['id']
        test_uri = '{}/{}/groups'.format(self.base_course_content_uri, unicode(self.course_project.scope_ids.usage_id))
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['group_id'], 2)

    def test_course_content_groups_detail_get(self):
        test_uri = '{}/{}/groups'.format(self.base_course_content_uri, unicode(self.course_project.scope_ids.usage_id))
        data = {'name': 'Alpha Group', 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        data = {'name': 'Beta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        response = self.do_get(response.data['uri'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['group_id'], str(group_id))

    def test_course_content_groups_detail_get_invalid_relationship(self):
        data = {'name': 'Alpha Group', 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/groups/{}'.format(self.base_course_content_uri, unicode(self.course_project.scope_ids.usage_id), group_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_detail_get_invalid_course(self):
        test_uri = '{}/{}/content/{}/groups/123456'.format(
            self.base_courses_uri,
            self.test_bogus_course_id,
            unicode(self.course_project.scope_ids.usage_id)
        )
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_detail_get_invalid_content(self):
        test_uri = '{}/{}/content/{}/groups/123456'.format(
            self.base_courses_uri,
            self.test_course_id,
            self.test_bogus_content_id
        )
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_groups_detail_get_invalid_group(self):
        test_uri = '{}/{}/content/{}/groups/123456'.format(
            self.base_courses_uri,
            self.test_course_id,
            unicode(self.course_project.scope_ids.usage_id)
        )
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_content_users_list_get(self):
        test_uri = '{}/{}/groups'.format(self.base_course_content_uri, unicode(self.course_project.scope_ids.usage_id))
        test_uri_users = '{}/{}/users'.format(self.base_course_content_uri, unicode(self.course_project.scope_ids.usage_id))
        test_course_users_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'

        # Create a group and add it to course module
        data = {'name': 'Alpha Group', 'type': 'test'}
        response = self.do_post(self.base_groups_uri, data)
        self.assertEqual(response.status_code, 201)
        group_id = response.data['id']
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        # Create another group and add it to course module
        data = {'name': 'Beta Group', 'type': 'project'}
        response = self.do_post(self.base_groups_uri, data)
        self.assertEqual(response.status_code, 201)
        another_group_id = response.data['id']
        data = {'group_id': another_group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        # create a 5 new users
        for i in xrange(1, 6):
            data = {
                'email': 'test{}@example.com'.format(i),
                'username': 'test_user{}'.format(i),
                'password': 'test_pass',
                'first_name': 'John{}'.format(i),
                'last_name': 'Doe{}'.format(i)
            }
            response = self.do_post(self.base_users_uri, data)
            self.assertEqual(response.status_code, 201)
            created_user_id = response.data['id']

            #add two users to Alpha Group and one to Beta Group and keep two without any group
            if i <= 3:
                add_to_group = group_id
                if i > 2:
                    add_to_group = another_group_id
                test_group_users_uri = '{}/{}/users'.format(self.base_groups_uri, add_to_group)

                data = {'user_id': created_user_id}
                response = self.do_post(test_group_users_uri, data)
                self.assertEqual(response.status_code, 201)
                #enroll one user in Alpha Group and one in Beta Group created user
                if i >= 2:
                    response = self.do_post(test_course_users_uri, data)
                    self.assertEqual(response.status_code, 201)
        response = self.do_get('{}?enrolled={}'.format(test_uri_users, 'True'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        response = self.do_get('{}?enrolled={}'.format(test_uri_users, 'False'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        #filter by group id
        response = self.do_get('{}?enrolled={}&group_id={}'.format(test_uri_users, 'true', group_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        response = self.do_get('{}?enrolled={}&group_id={}'.format(test_uri_users, 'false', group_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        #filter by group type
        response = self.do_get('{}?enrolled={}&type={}'.format(test_uri_users, 'true', 'project'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_course_content_users_list_get_invalid_course_and_content(self):
        invalid_course_uri = '{}/{}/content/{}/users'.format(self.base_courses_uri, self.test_bogus_course_id, unicode(self.course_project.scope_ids.usage_id))
        response = self.do_get(invalid_course_uri)
        self.assertEqual(response.status_code, 404)

        invalid_content_uri = '{}/{}/content/{}/users'.format(self.base_courses_uri, self.test_course_id, self.test_bogus_content_id)
        response = self.do_get(invalid_content_uri)
        self.assertEqual(response.status_code, 404)

    def test_coursemodulecompletions_post(self):

        data = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'test_pass',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.do_post(self.base_users_uri, data)
        self.assertEqual(response.status_code, 201)
        created_user_id = response.data['id']
        completions_uri = '{}/{}/completions/'.format(self.base_courses_uri, unicode(self.course.id))
        stage = 'First'
        completions_data = {'content_id': unicode(self.course_content.scope_ids.usage_id), 'user_id': created_user_id, 'stage': stage}
        response = self.do_post(completions_uri, completions_data)
        self.assertEqual(response.status_code, 201)
        coursemodulecomp_id = response.data['id']
        self.assertGreater(coursemodulecomp_id, 0)
        self.assertEqual(response.data['user_id'], created_user_id)
        self.assertEqual(response.data['course_id'], unicode(self.course.id))
        self.assertEqual(response.data['content_id'], unicode(self.course_content.scope_ids.usage_id))
        self.assertEqual(response.data['stage'], stage)
        self.assertIsNotNone(response.data['created'])
        self.assertIsNotNone(response.data['modified'])

        # test to create course completion with same attributes
        response = self.do_post(completions_uri, completions_data)
        self.assertEqual(response.status_code, 409)

        # test to create course completion with empty user_id
        completions_data['user_id'] = None
        response = self.do_post(completions_uri, completions_data)
        self.assertEqual(response.status_code, 400)

        # test to create course completion with empty content_id
        completions_data['content_id'] = None
        response = self.do_post(completions_uri, completions_data)
        self.assertEqual(response.status_code, 400)

        # test to create course completion with invalid content_id
        completions_data['content_id'] = self.test_bogus_content_id
        response = self.do_post(completions_uri, completions_data)
        self.assertEqual(response.status_code, 400)

    def test_course_module_completions_post_invalid_course(self):
        completions_uri = '{}/{}/completions/'.format(self.base_courses_uri, self.test_bogus_course_id)
        completions_data = {'content_id': unicode(self.course_content.scope_ids.usage_id), 'user_id': self.users[0].id}
        response = self.do_post(completions_uri, completions_data)
        self.assertEqual(response.status_code, 404)

    def test_course_module_completions_post_invalid_content(self):
        completions_uri = '{}/{}/completions/'.format(self.base_courses_uri, self.test_course_id)
        completions_data = {'content_id': self.test_bogus_content_id, 'user_id': self.users[0].id}
        response = self.do_post(completions_uri, completions_data)
        self.assertEqual(response.status_code, 400)

    def test_coursemodulecompletions_filters(self):
        completion_uri = '{}/{}/completions/'.format(self.base_courses_uri, unicode(self.course.id))
        for i in xrange(1, 3):
            data = {
                'email': 'test{}@example.com'.format(i),
                'username': 'test_user{}'.format(i),
                'password': 'test_pass',
                'first_name': 'John{}'.format(i),
                'last_name': 'Doe{}'.format(i)
            }
            response = self.do_post(self.base_users_uri, data)
            self.assertEqual(response.status_code, 201)
            created_user_id = response.data['id']

        for i in xrange(1, 26):
            local_content_name = 'Video_Sequence{}'.format(i)
            local_content = ItemFactory.create(
                category="videosequence",
                parent_location=self.chapter.location,
                data=self.test_data,
                display_name=local_content_name
            )
            content_id = unicode(local_content.scope_ids.usage_id)
            if i < 25:
                content_id = unicode(self.course_content.scope_ids.usage_id) + str(i)
                stage = None
            else:
                content_id = unicode(self.course_content.scope_ids.usage_id)
                stage = 'Last'
            completions_data = {'content_id': content_id, 'user_id': created_user_id, 'stage': stage}
            response = self.do_post(completion_uri, completions_data)
            self.assertEqual(response.status_code, 201)

        #filter course module completion by user
        user_filter_uri = '{}?user_id={}&page_size=10&page=3'.format(completion_uri, created_user_id)
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['num_pages'], 3)

        #filter course module completion by multiple user ids
        user_filter_uri = '{}?user_id={}'.format(completion_uri, str(created_user_id) + ',10001,10003')
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 20)
        self.assertEqual(response.data['num_pages'], 2)

        #filter course module completion by user who has not completed any course module
        user_filter_uri = '{}?user_id={}'.format(completion_uri, 10001)
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        #filter course module completion by course_id
        course_filter_uri = '{}?course_id={}&page_size=10'.format(completion_uri, unicode(self.course.id))
        response = self.do_get(course_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 10)

        #filter course module completion by content_id
        content_id = {'content_id': '{}1'.format(unicode(self.course_content.scope_ids.usage_id))}
        content_filter_uri = '{}?{}'.format(completion_uri, urlencode(content_id))
        response = self.do_get(content_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

        #filter course module completion by invalid content_id
        content_id = {'content_id': '{}1'.format(self.test_bogus_content_id)}
        content_filter_uri = '{}?{}'.format(completion_uri, urlencode(content_id))
        response = self.do_get(content_filter_uri)
        self.assertEqual(response.status_code, 404)

        #filter course module completion by stage
        content_filter_uri = '{}?stage={}'.format(completion_uri, 'Last')
        response = self.do_get(content_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

    def test_coursemodulecompletions_get_invalid_course(self):
        completion_uri = '{}/{}/completions/'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(completion_uri)
        self.assertEqual(response.status_code, 404)

    @mock.patch("api_manager.courses.views.get_course_social_stats", _fake_get_course_social_stats_date_expected)
    def test_courses_metrics_social_get(self):
        test_uri = '{}/{}/metrics/social/'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.keys()), 2)
        users = response.data['users']
        self.assertIn('2', users)
        self.assertIn('3', users)

        # make the first user an observer to asset that its content is being filtered out from
        # the aggregates
        allow_access(self.course, self.users[0], 'observer')

        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.keys()), 2)
        users = response.data['users']
        self.assertNotIn('2', users)
        self.assertIn('3', users)

    @mock.patch("api_manager.courses.views.get_course_social_stats", _fake_get_course_social_stats)
    def test_courses_metrics_social_get_no_date(self):
        course = CourseFactory.create(
            start=datetime(2014, 6, 16, 14, 30)
        )
        USER_COUNT = 2
        users = [UserFactory.create(username="coursesmetrics_user" + str(__), profile='test') for __ in xrange(USER_COUNT)]
        for user in users:
            CourseEnrollmentFactory.create(user=user, course_id=course.id)

        test_uri = '{}/{}/metrics/social/'.format(self.base_courses_uri, unicode(course.id))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data.keys()), 2)
        result_users = response.data['users']
        # expect all users are in result set
        for user in users:
            self.assertTrue(result_users.get(str(user.id)))

    def test_courses_metrics_grades_leaders_list_get(self):
        # setup data for course metrics grades leaders
        data = self._setup_courses_metrics_grades_leaders()
        expected_course_average = 0.398

        test_uri = '{}/{}/metrics/grades/leaders/'.format(self.base_courses_uri, unicode(data['course'].id))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 3)
        self.assertEqual(response.data['leaders'][0]['username'], 'testleaderuser4')
        self.assertEqual(response.data['course_avg'], expected_course_average)

        count_filter_test_uri = '{}?count=4'.format(test_uri)
        response = self.do_get(count_filter_test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 4)

        # Filter by user_id, include a user with the exact same score
        user200 = UserFactory.create(username="testuser200", profile='test')
        CourseEnrollmentFactory.create(user=user200, course_id=data['course'].id)

        midterm = ItemFactory.create(
            parent_location=data['chapter'].location,
            category='problem',
            data=StringResponseXMLFactory().build_xml(answer='bar'),
            display_name='Problem 200',
            metadata={'rerandomize': 'always', 'graded': True, 'format': 'Midterm Exam'}
        )
        points_scored = 100
        points_possible = 100
        module = self.get_module_for_user(user200, data['course'], midterm)
        grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user200.id}
        module.system.publish(module, 'grade', grade_dict)
        StudentModuleFactory.create(
            course_id=data['course'].id,
            module_type='sequential',
            module_state_key=midterm.location,
        )
        final = ItemFactory.create(
            parent_location=data['chapter'].location,
            category='problem',
            data=StringResponseXMLFactory().build_xml(answer='bar'),
            display_name='Problem 201',
            metadata={'rerandomize': 'always', 'graded': True, 'format': 'Final Exam'}
        )
        points_scored = 100
        points_possible = 100
        module = self.get_module_for_user(user200, data['course'], final)
        grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user200.id}
        module.system.publish(module, 'grade', grade_dict)
        StudentModuleFactory.create(
            course_id=data['course'].id,
            module_type='sequential',
            module_state_key=final.location,
        )
        points_scored = 50
        points_possible = 100
        module = self.get_module_for_user(user200, data['course'], data['item'])
        grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user200.id}
        module.system.publish(module, 'grade', grade_dict)

        user_filter_uri = '{}?user_id={}&count=10'.format(test_uri, data['users'][1].id)
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 6)
        self.assertEqual(response.data['course_avg'], 0.378)
        self.assertEqual(response.data['user_position'], 4)
        self.assertEqual(response.data['user_grade'], 0.28)

        # Filter by user who has never accessed a course module
        test_user = UserFactory.create(username="testusernocoursemod")
        CourseEnrollmentFactory.create(user=test_user, course_id=data['course'].id)
        user_filter_uri = '{}?user_id={}'.format(test_uri, test_user.id)
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_grade'], 0)
        self.assertEqual(response.data['user_position'], 7)
        # Also, with this new user now added the course average should be different
        self.assertNotEqual(response.data['course_avg'], expected_course_average)
        rounded_avg = float("{0:.2f}".format(response.data['course_avg']))
        self.assertEqual(rounded_avg, 0.32)

        # test with bogus course
        bogus_test_uri = '{}/{}/metrics/grades/leaders/'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(bogus_test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_metrics_grades_leaders_list_get_filter_by_group(self):
        # setup data for course metrics grades leaders
        data = self._setup_courses_metrics_grades_leaders()
        expected_course_average = 0.398

        test_uri = '{}/{}/metrics/grades/leaders/?groups={}'.format(self.base_courses_uri,
                                                                    unicode(data['course'].id),
                                                                    data['groups'][0].id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 3)
        self.assertEqual(response.data['leaders'][0]['username'], 'testleaderuser4')
        self.assertEqual(response.data['course_avg'], expected_course_average)

        count_filter_test_uri = '{}&count=10'.format(test_uri)
        response = self.do_get(count_filter_test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 3)

        user_filter_uri = '{}&user_id={}&count=10'.format(test_uri, data['users'][1].id)
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 3)
        self.assertEqual(response.data['course_avg'], expected_course_average)
        self.assertEqual(response.data['user_position'], 3)
        self.assertEqual(response.data['user_grade'], 0.28)

    def test_courses_metrics_grades_leaders_list_get_filter_by_multiple_group(self):
        # setup data for course metrics grades leaders
        data = self._setup_courses_metrics_grades_leaders()
        expected_course_average = 0.398
        group_ids = ','.join([str(group.id) for group in data['groups']])

        test_uri = '{}/{}/metrics/grades/leaders/?groups={}'.format(self.base_courses_uri,
                                                                    unicode(data['course'].id),
                                                                    group_ids)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 3)
        self.assertEqual(response.data['leaders'][0]['username'], 'testleaderuser4')
        self.assertEqual(response.data['course_avg'], expected_course_average)

        count_filter_test_uri = '{}&count=10'.format(test_uri)
        response = self.do_get(count_filter_test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 5)

        user_filter_uri = '{}&user_id={}&count=10'.format(test_uri, data['users'][1].id)
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 5)
        self.assertEqual(response.data['course_avg'], expected_course_average)
        self.assertEqual(response.data['user_position'], 4)
        self.assertEqual(response.data['user_grade'], 0.28)

    def test_courses_metrics_grades_leaders_list_get_empty_course(self):
        test_uri = '{}/{}/metrics/grades/leaders/'.format(self.base_courses_uri, unicode(self.empty_course.id))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['course_avg'], 0)
        self.assertEqual(len(response.data['leaders']), 0)

    def test_courses_completions_leaders_list_get(self):
        setup_data = self._setup_courses_completions_leaders()
        expected_course_avg = '25.000'
        test_uri = '{}?count=6'.format(setup_data['leaders_uri'])
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 4)
        self.assertEqual('{0:.3f}'.format(response.data['course_avg']), expected_course_avg)

        # without count filter and user_id
        test_uri = '{}?user_id={}'.format(setup_data['leaders_uri'], setup_data['users'][1].id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 4)
        self.assertEqual(response.data['position'], 2)
        self.assertEqual('{0:.3f}'.format(response.data['completions']), '28.000')

        # with skipleaders filter
        test_uri = '{}?user_id={}&skipleaders=true'.format(setup_data['leaders_uri'], setup_data['users'][1].id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data.get('leaders', None))
        self.assertEqual('{0:.3f}'.format(response.data['course_avg']), expected_course_avg)
        self.assertEqual('{0:.3f}'.format(response.data['completions']), '28.000')

        # test with bogus course
        test_uri = '{}/{}/metrics/completions/leaders/'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

        #filter course module completion by organization
        data = {
            'name': 'Test Organization',
            'display_name': 'Test Org Display Name',
            'users': [setup_data['users'][1].id]
        }
        response = self.do_post(self.base_organizations_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = '{}?organizations={}'.format(setup_data['leaders_uri'], response.data['id'])
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 1)
        self.assertEqual(response.data['leaders'][0]['id'], setup_data['users'][1].id)
        self.assertEqual('{0:.3f}'.format(response.data['leaders'][0]['completions']), '28.000')
        self.assertEqual('{0:.3f}'.format(response.data['course_avg']), '28.000')

        # test with unknown user
        test_uri = '{}?user_id={}&skipleaders=true'.format(setup_data['leaders_uri'], '909999')
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data.get('leaders', None))
        self.assertEqual(response.data['position'], 0)
        self.assertEqual(response.data['completions'], 0)

        # test a case where completions are greater than total course modules. it should not be more than 100
        setup_data['contents'].append(self.course_content)
        for content in setup_data['contents'][2:]:
            user_id = setup_data['users'][0].id
            content_id = unicode(content.scope_ids.usage_id)
            completions_data = {'content_id': content_id, 'user_id': user_id}
            response = self.do_post(setup_data['completion_uri'], completions_data)
            self.assertEqual(response.status_code, 201)

        test_uri = '{}?user_id={}'.format(setup_data['leaders_uri'], setup_data['users'][0].id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('{0:.3f}'.format(response.data['completions']), '100.000')

    def test_courses_completions_leaders_list_get_filter_users_by_group(self):
        """
        Test courses completions leaders with group filter
        """
        setup_data = self._setup_courses_completions_leaders()
        expected_course_avg = '18.000'
        test_uri = '{}?groups={}'.format(setup_data['leaders_uri'], setup_data['groups'][0].id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 2)
        self.assertEqual('{0:.3f}'.format(response.data['course_avg']), expected_course_avg)

    def test_courses_completions_leaders_list_get_filter_users_by_multiple_groups(self):
        """
        Test courses completions leaders with group filter for users in multiple groups
        """
        setup_data = self._setup_courses_completions_leaders()
        expected_course_avg = '25.000'
        group_ids = ','.join([str(group.id) for group in setup_data['groups']])
        test_uri = '{}?groups={}'.format(setup_data['leaders_uri'], group_ids)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['leaders']), 4)
        self.assertEqual('{0:.3f}'.format(response.data['course_avg']), expected_course_avg)

    def test_courses_metrics_grades_list_get(self):
        # Retrieve the list of grades for this course
        # All the course/item/user scaffolding was handled in Setup
        test_uri = '{}/{}/metrics/grades'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data['grade_average'], 0)
        self.assertGreater(response.data['grade_maximum'], 0)
        self.assertGreater(response.data['grade_minimum'], 0)
        self.assertEqual(response.data['grade_count'], USER_COUNT)
        self.assertGreater(response.data['course_grade_average'], 0)
        self.assertGreater(response.data['course_grade_maximum'], 0)
        self.assertGreater(response.data['course_grade_minimum'], 0)
        self.assertEqual(response.data['course_grade_count'], USER_COUNT)
        self.assertEqual(len(response.data['grades']), USER_COUNT)

        # Filter by user_id
        user_filter_uri = '{}?user_id=2,4'.format(test_uri)
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data['grade_average'], 0)
        self.assertGreater(response.data['grade_maximum'], 0)
        self.assertGreater(response.data['grade_minimum'], 0)
        self.assertEqual(response.data['grade_count'], 2)
        self.assertGreater(response.data['course_grade_average'], 0)
        self.assertGreater(response.data['course_grade_maximum'], 0)
        self.assertGreater(response.data['course_grade_minimum'], 0)
        self.assertEqual(response.data['course_grade_count'], USER_COUNT)
        self.assertEqual(len(response.data['grades']), 2)

        # make the last user an observer to asset that its content is being filtered out from
        # the aggregates
        user_index = USER_COUNT - 1
        allow_access(self.course, self.users[user_index], 'observer')
        test_uri = '{}/{}/metrics/grades'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['grades']), user_index)

    def test_courses_metrics_grades_list_get_filter_users_by_group(self):
        # Retrieve the list of grades for course and filter by groups
        groups = GroupFactory.create_batch(2)
        users = UserFactory.create_batch(5)

        for i, user in enumerate(users):
            user.groups.add(groups[i % 2])

        for user in users:
            CourseEnrollmentFactory.create(user=user, course_id=self.course.id)

        for j, user in enumerate(users):
            points_scored = (j + 1) * 20
            points_possible = 100
            module = self.get_module_for_user(user, self.course, self.item)
            grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user.id}
            module.system.publish(module, 'grade', grade_dict)

        user_ids = ','.join([str(user.id) for user in users])
        test_uri = '{}/{}/metrics/grades?user_id={}&groups={}'.format(self.base_courses_uri,
                                                                      self.test_course_id,
                                                                      user_ids,
                                                                      groups[0].id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data['grade_average'], 0)
        self.assertGreater(response.data['grade_maximum'], 0)
        self.assertGreater(response.data['grade_minimum'], 0)
        self.assertEqual(response.data['grade_count'], 3)
        self.assertGreater(response.data['course_grade_average'], 0)
        self.assertGreater(response.data['course_grade_maximum'], 0)
        self.assertGreater(response.data['course_grade_minimum'], 0)
        self.assertEqual(response.data['course_grade_count'], USER_COUNT + 5)
        self.assertEqual(len(response.data['grades']), 3)

    def test_courses_metrics_grades_list_get_filter_users_by_multiple_groups(self):
        # Retrieve the list of grades for course and filter by multiple groups and user_id
        groups = GroupFactory.create_batch(2)
        users = UserFactory.create_batch(5)

        for i, user in enumerate(users):
            user.groups.add(groups[i % 2])

        users[0].groups.add(groups[1])

        for user in users:
            CourseEnrollmentFactory.create(user=user, course_id=self.course.id)

        for j, user in enumerate(users):
            points_scored = (j + 1) * 20
            points_possible = 100
            module = self.get_module_for_user(user, self.course, self.item)
            grade_dict = {'value': points_scored, 'max_value': points_possible, 'user_id': user.id}
            module.system.publish(module, 'grade', grade_dict)

        user_ids = ','.join([str(user.id) for user in users])
        test_uri = '{}/{}/metrics/grades'.format(self.base_courses_uri, self.test_course_id,)
        user_group_filter_uri = '{}?user_id={}&groups={},{}'.format(test_uri,
                                                                    user_ids,
                                                                    groups[0].id,
                                                                    groups[1].id)
        response = self.do_get(user_group_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data['grade_average'], 0)
        self.assertGreater(response.data['grade_maximum'], 0)
        self.assertGreater(response.data['grade_minimum'], 0)
        self.assertEqual(response.data['grade_count'], 5)
        self.assertGreater(response.data['course_grade_average'], 0)
        self.assertGreater(response.data['course_grade_maximum'], 0)
        self.assertGreater(response.data['course_grade_minimum'], 0)
        self.assertEqual(response.data['course_grade_count'], USER_COUNT + 5)
        self.assertEqual(len(response.data['grades']), 5)

    def test_courses_metrics_grades_list_get_empty_course(self):
        # Retrieve the list of grades for this course
        # All the course/item/user scaffolding was handled in Setup
        test_uri = '{}/{}/metrics/grades'.format(self.base_courses_uri, unicode(self.empty_course.id))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['grade_count'], 0)
        self.assertEqual(response.data['course_grade_maximum'], 0)

    def test_courses_grades_list_get_invalid_course(self):
        # Retrieve the list of grades for this course
        # All the course/item/user scaffolding was handled in Setup
        test_uri = '{}/{}/grades'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_project_list(self):
        projects_uri = self.base_projects_uri

        for i in xrange(0, 25):
            local_content_name = 'Video_Sequence{}'.format(i)
            local_content = ItemFactory.create(
                category="videosequence",
                parent_location=self.chapter.location,
                data=self.test_data,
                display_name=local_content_name
            )
            data = {
                'content_id': unicode(local_content.scope_ids.usage_id),
                'course_id': self.test_course_id
            }
            response = self.do_post(projects_uri, data)
            self.assertEqual(response.status_code, 201)

        response = self.do_get('{}/{}/projects/?page_size=10'.format(self.base_courses_uri, self.test_course_id))
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['num_pages'], 3)

    def test_courses_data_metrics(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        completion_uri = '{}/{}/completions/'.format(self.base_courses_uri, unicode(self.course.id))
        test_user_uri = self.base_users_uri
        users_to_add = 5
        for i in xrange(0, users_to_add):
            data = {
                'email': 'test{}@example.com'.format(i), 'username': 'tcdm_user{}'.format(i),
                'password': 'test_password'
            }
            # create a new user
            response = self.do_post(test_user_uri, data)
            self.assertEqual(response.status_code, 201)
            created_user_id = response.data['id']

            # now enroll this user in the course
            post_data = {'user_id': created_user_id}
            response = self.do_post(test_uri, post_data)
            self.assertEqual(response.status_code, 201)

        #create an organization
        data = {
            'name': 'Test Organization',
            'display_name': 'Test Org Display Name',
            'users': [created_user_id]
        }
        response = self.do_post(self.base_organizations_uri, data)
        self.assertEqual(response.status_code, 201)
        org_id = response.data['id']

        for i in xrange(1, users_to_add):
            local_content_name = 'Video_Sequence{}'.format(i)
            local_content = ItemFactory.create(
                category="videosequence",
                parent_location=self.content_child2.location,
                data=self.test_data,
                display_name=local_content_name
            )
            content_id = unicode(local_content.scope_ids.usage_id)
            completions_data = {'content_id': content_id, 'user_id': created_user_id, 'stage': None}
            response = self.do_post(completion_uri, completions_data)
            self.assertEqual(response.status_code, 201)

        # get course metrics
        course_metrics_uri = '{}/{}/metrics/'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['users_enrolled'], users_to_add + USER_COUNT)
        self.assertGreaterEqual(response.data['users_started'], 1)
        self.assertEqual(response.data['users_not_started'], users_to_add + USER_COUNT - 1)
        self.assertEqual(response.data['modules_completed'], users_to_add - 1)
        self.assertEqual(response.data['users_completed'], 0)
        self.assertIsNotNone(response.data['grade_cutoffs'])
        self.assertEqual(response.data['num_threads'], 5)
        self.assertEqual(response.data['num_active_threads'], 3)

        # get course metrics by organization
        course_metrics_uri = '{}/{}/metrics/?organization={}'.format(
            self.base_courses_uri,
            self.test_course_id,
            org_id
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['users_enrolled'], 1)
        self.assertGreaterEqual(response.data['users_started'], 1)

        # test with bogus course
        course_metrics_uri = '{}/{}/metrics/'.format(
            self.base_courses_uri,
            self.test_bogus_course_id
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_data_metrics_user_group_filter_for_empty_group(self):
        group = GroupFactory.create()

        # get course metrics for users in group
        course_metrics_uri = '{}/{}/metrics/?groups={}'.format(
            self.base_courses_uri,
            self.test_course_id,
            group.id
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['users_enrolled'], 0)
        self.assertGreaterEqual(response.data['users_started'], 0)

    def test_course_data_metrics_user_group_filter_for_group_having_members(self):
        group = GroupFactory.create()
        users = UserFactory.create_batch(3, groups=(group,))

        # enroll all users in course
        for user in users:
            CourseEnrollmentFactory.create(user=user, course_id=self.course.id)

        # create course completions
        for i, user in enumerate(users):
            completions_uri = '{}/{}/completions/'.format(self.base_courses_uri, self.test_course_id)
            completions_data = {
                'content_id': unicode(self.course_content.scope_ids.usage_id),
                'user_id': user.id,
                'stage': 'First'
            }
            response = self.do_post(completions_uri, completions_data)
            self.assertEqual(response.status_code, 201)

            # mark two users a complete
            if i % 2 == 0:
                StudentGradebook.objects.get_or_create(
                    user=user,
                    course_id=self.course.id,
                    grade=0.9,
                    proforma_grade=0.91,
                )

        course_metrics_uri = '{}/{}/metrics/?groups={}'.format(
            self.base_courses_uri,
            self.test_course_id,
            group.id
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['users_enrolled'], 3)
        self.assertGreaterEqual(response.data['users_started'], 3)
        self.assertEqual(response.data['users_not_started'], 0)
        self.assertEqual(response.data['modules_completed'], 3)
        self.assertEqual(response.data['users_completed'], 2)

    def test_course_data_metrics_user_group_filter_for_multiple_groups_having_members(self):
        groups = GroupFactory.create_batch(2)
        users = UserFactory.create_batch(4, groups=(groups[0],))
        users.append(UserFactory.create(groups=groups))

        # enroll all users in course
        for user in users:
            CourseEnrollmentFactory.create(user=user, course_id=self.course.id)

        # create course completions
        for user in users:
            completions_uri = '{}/{}/completions/'.format(self.base_courses_uri, self.test_course_id)
            completions_data = {
                'content_id': unicode(self.course_content.scope_ids.usage_id),
                'user_id': user.id,
                'stage': 'First'
            }
            response = self.do_post(completions_uri, completions_data)
            self.assertEqual(response.status_code, 201)

        course_metrics_uri = '{}/{}/metrics/?groups={},{}'.format(
            self.base_courses_uri,
            self.test_course_id,
            groups[0].id,
            groups[1].id,
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['users_enrolled'], 5)
        self.assertGreaterEqual(response.data['users_started'], 5)
        self.assertEqual(response.data['users_not_started'], 0)
        self.assertEqual(response.data['modules_completed'], 5)
        self.assertEqual(response.data['users_completed'], 0)

    def test_course_workgroups_list(self):
        projects_uri = self.base_projects_uri
        data = {
            'course_id': self.test_course_id,
            'content_id': 'self.test_course_content_id'
        }
        response = self.do_post(projects_uri, data)
        self.assertEqual(response.status_code, 201)
        project_id = response.data['id']

        test_workgroups_uri = self.base_workgroups_uri
        for i in xrange(1, 12):
            data = {
                'name': '{} {}'.format('Workgroup', i),
                'project': project_id
            }
            response = self.do_post(test_workgroups_uri, data)
            self.assertEqual(response.status_code, 201)

        # get workgroups associated to course
        test_uri = '{}/{}/workgroups/?page_size=10'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.data['count'], 11)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['num_pages'], 2)

        # test with bogus course
        test_uri = '{}/{}/workgroups/'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_users_count_by_city(self):
        test_uri = self.base_users_uri

        # create a 25 new users
        for i in xrange(1, 26):
            if i < 10:
                city = 'San Francisco'
            elif i < 15:
                city = 'Denver'
            elif i < 20:
                city = 'Dallas'
            else:
                city = 'New York City'
            data = {
                'email': 'test{}@example.com'.format(i), 'username': 'test_user{}'.format(i),
                'password': 'test.me!',
                'first_name': '{} {}'.format('John', i), 'last_name': '{} {}'.format('Doe', i), 'city': city,
                'country': 'PK', 'level_of_education': 'b', 'year_of_birth': '2000', 'gender': 'male',
                'title': 'Software Engineer', 'avatar_url': 'http://example.com/avatar.png'
            }

            response = self.do_post(test_uri, data)
            self.assertEqual(response.status_code, 201)
            created_user_id = response.data['id']
            user_uri = response.data['uri']
            # now enroll this user in the course
            post_data = {'user_id': created_user_id}
            courses_test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
            response = self.do_post(courses_test_uri, post_data)
            self.assertEqual(response.status_code, 201)

            response = self.do_get(user_uri)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['city'], city)

        # make all the classwide users an observer to assert that its content is being filtered out from
        # the aggregates
        for user in self.users:
            allow_access(self.course, user, 'observer')

        response = self.do_get('{}/{}/metrics/cities/'.format(self.base_courses_uri, self.test_course_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 4)
        self.assertEqual(response.data['results'][0]['city'], 'San Francisco')
        self.assertEqual(response.data['results'][0]['count'], 9)

        # filter counts by city
        sf_uri = '{}/{}/metrics/cities/?city=new york city, San Francisco'.format(self.base_courses_uri,
                                                                                  self.test_course_id)
        response = self.do_get(sf_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['city'], 'San Francisco')
        self.assertEqual(response.data['results'][0]['count'], 9)
        self.assertEqual(response.data['results'][1]['city'], 'New York City')
        self.assertEqual(response.data['results'][1]['count'], 6)

        # filter counts by city
        dnv_uri = '{}/{}/metrics/cities/?city=Denver'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(dnv_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['city'], 'Denver')
        self.assertEqual(response.data['results'][0]['count'], 5)

        # Do a get with a bogus course to hit the 404 case
        response = self.do_get('{}/{}/metrics/cities/'.format(self.base_courses_uri, self.test_bogus_course_id))
        self.assertEqual(response.status_code, 404)

    def test_courses_roles_list_get(self):
        allow_access(self.course, self.users[0], 'staff')
        allow_access(self.course, self.users[1], 'instructor')
        allow_access(self.course, self.users[2], 'observer')
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, unicode(self.course.id))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # filter roleset by user
        user_id = {'user_id': '{}'.format(self.users[0].id)}
        user_filter_uri = '{}?{}'.format(test_uri, urlencode(user_id))
        response = self.do_get(user_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # filter roleset by role
        role = {'role': 'instructor'}
        role_filter_uri = '{}?{}'.format(test_uri, urlencode(role))
        response = self.do_get(role_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        role = {'role': 'invalid_role'}
        role_filter_uri = '{}?{}'.format(test_uri, urlencode(role))
        response = self.do_get(role_filter_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_courses_roles_list_get_invalid_course(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_roles_list_post(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, unicode(self.course.id))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        data = {'user_id': self.users[0].id, 'role': 'instructor'}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # Confirm this user also has forum moderation permissions
        role = Role.objects.get(course_id=self.course.id, name=FORUM_ROLE_MODERATOR)
        has_role = role.users.get(id=self.users[0].id)
        self.assertTrue(has_role)

    def test_courses_roles_list_post_invalid_course(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, self.test_bogus_course_id)
        data = {'user_id': self.users[0].id, 'role': 'instructor'}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 404)

    def test_courses_roles_list_post_invalid_user(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, unicode(self.course.id))
        data = {'user_id': 23423, 'role': 'instructor'}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 400)

    def test_courses_roles_list_post_invalid_role(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, unicode(self.course.id))
        data = {'user_id': self.users[0].id, 'role': 'invalid_role'}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 400)

    def test_courses_roles_users_detail_delete(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, unicode(self.course.id))
        data = {'user_id': self.users[0].id, 'role': 'instructor'}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)

        response = self.do_get(test_uri)
        self.assertEqual(len(response.data), 1)

        delete_uri = '{}instructor/users/{}'.format(test_uri, self.users[0].id)
        response = self.do_delete(delete_uri)
        self.assertEqual(response.status_code, 204)

        response = self.do_get(test_uri)
        self.assertEqual(len(response.data), 0)

        # Confirm this user no longer has forum moderation permissions
        role = Role.objects.get(course_id=self.course.id, name=FORUM_ROLE_MODERATOR)
        try:
            role.users.get(id=self.users[0].id)
            self.assertTrue(False)
        except ObjectDoesNotExist:
            pass

    def test_courses_roles_users_detail_delete_invalid_course(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, self.test_bogus_course_id)
        delete_uri = '{}instructor/users/{}'.format(test_uri, self.users[0].id)
        response = self.do_delete(delete_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_roles_users_detail_delete_invalid_user(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, unicode(self.course.id))
        delete_uri = '{}instructor/users/291231'.format(test_uri)
        response = self.do_delete(delete_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_roles_users_detail_delete_invalid_role(self):
        test_uri = '{}/{}/roles/'.format(self.base_courses_uri, unicode(self.course.id))
        delete_uri = '{}invalid_role/users/{}'.format(test_uri, self.users[0].id)
        response = self.do_delete(delete_uri)
        self.assertEqual(response.status_code, 404)

    def test_course_navigation(self):
        test_uri = '{}/{}/navigation/{}'.format(
            self.base_courses_uri, unicode(self.course.id), self.content_subchild.location.block_id
        )
        response = self.do_get(test_uri)
        self.assertEqual(
            {
                'chapter': unicode(self.chapter.location),
                'vertical': unicode(self.content_child2.location),
                'section': unicode(self.course_content2.location),
                'course_key': unicode(self.course.id),
                'final_target_id': unicode(self.content_subchild.location),
                'position': '1',
            },
            response.data
        )


@override_settings(MODULESTORE=MODULESTORE_CONFIG)
@override_settings(EDX_API_KEY=TEST_API_KEY)
@mock.patch.dict("django.conf.settings.FEATURES", {'ENFORCE_PASSWORD_POLICY': False,
                                                   'ADVANCED_SECURITY': False,
                                                   'PREVENT_CONCURRENT_LOGINS': False,
                                                   'MARK_PROGRESS_ON_GRADING_EVENT': True,
                                                   'SIGNAL_ON_SCORE_CHANGED': True,
                                                   'STUDENT_GRADEBOOK': True,
                                                   'STUDENT_PROGRESS': True})
class CoursesTimeSeriesMetricsApiTests(ModuleStoreTestCase):
    """ Test suite for CoursesTimeSeriesMetrics API views """

    def get_module_for_user(self, user, course, problem):
        """Helper function to get useful module at self.location in self.course_id for user"""
        mock_request = mock.MagicMock()
        mock_request.user = user
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            course.id, user, course, depth=2)
        module = module_render.get_module(  # pylint: disable=protected-access
            user,
            mock_request,
            problem.location,
            field_data_cache,
        )
        return module

    def setUp(self):
        super(CoursesTimeSeriesMetricsApiTests, self).setUp()
        self.test_server_prefix = 'https://testserver'
        self.base_courses_uri = '/api/server/courses'
        self.base_groups_uri = '/api/server/groups'
        self.base_organizations_uri = '/api/server/organizations/'
        self.test_data = '<html>{}</html>'.format(str(uuid.uuid4()))

        self.reference_date = datetime(2015, 8, 21, 0, 0, 0, 0, pytz.UTC)
        course_start_date = self.reference_date + relativedelta(months=-2)
        course_end_date = self.reference_date + relativedelta(years=5)

        # Set up two courses, complete with chapters, sections, units, and items
        self.course = CourseFactory.create(
            number='3033',
            name='metrics_in_timeseries',
            start=course_start_date,
            end=course_end_date
        )

        self.second_course = CourseFactory.create(
            number='3034',
            name='metrics_in_timeseries2',
            start=course_start_date,
            end=course_end_date
        )

        self.chapter = ItemFactory.create(
            category="chapter",
            parent_location=self.course.location,
            data=self.test_data,
            due=course_end_date,
            display_name=u"3033 Overview"
        )

        self.sub_section = ItemFactory.create(
            parent_location=self.chapter.location,
            category="sequential",
            display_name="3033 test subsection",
        )
        self.unit = ItemFactory.create(
            parent_location=self.sub_section.location,
            category="vertical",
            metadata={'graded': True, 'format': 'Homework'},
            display_name=u"3033 test unit",
        )

        self.item = ItemFactory.create(
            parent_location=self.unit.location,
            category='problem',
            data=StringResponseXMLFactory().build_xml(answer='bar'),
            display_name='Problem to test timeseries',
            metadata={'rerandomize': 'always', 'graded': True, 'format': 'Midterm Exam'}
        )

        self.item2 = ItemFactory.create(
            parent_location=self.unit.location,
            category='problem',
            data=StringResponseXMLFactory().build_xml(answer='bar'),
            display_name='Problem 2 for test timeseries',
            metadata={'rerandomize': 'always', 'graded': True, 'format': 'Final Exam'}
        )

        # Create the set of users that will enroll in these courses
        self.user_count = 25
        self.users = UserFactory.create_batch(self.user_count)
        self.groups = GroupFactory.create_batch(2)
        self.user_ids = []
        for i, user in enumerate(self.users):
            self.user_ids.append(user.id)
            user.groups.add(self.groups[i % 2])

        self.users[0].groups.add(self.groups[1])

        # Create a test organization that will be used for validation of org filtering
        self.test_organization = Organization.objects.create(
            name="Test Organization",
            display_name='Test Org Display Name',
        )
        self.test_organization.users.add(*self.users)
        self.org_id = self.test_organization.id

        # Enroll the users in the courses using an old datestamp
        enrolled_time = self.reference_date - timedelta(days=self.user_count, minutes=-30)
        with freeze_time(enrolled_time):
            for user in self.users:
                CourseEnrollmentFactory.create(user=user, course_id=self.course.id)
                CourseEnrollmentFactory.create(user=user, course_id=self.second_course.id)

        # Set up the basic score container that will be used for student submissions
        points_scored = .25
        points_possible = 1
        self.grade_dict = {'value': points_scored, 'max_value': points_possible}

        self.client = SecureClient()
        cache.clear()

    def do_get(self, uri):
        """Submit an HTTP GET request"""
        headers = {
            'Content-Type': 'application/json',
            'X-Edx-Api-Key': str(TEST_API_KEY),
        }
        response = self.client.get(uri, headers=headers)
        return response

    def do_post(self, uri, data):
        """Submit an HTTP POST request"""
        headers = {
            'X-Edx-Api-Key': str(TEST_API_KEY),
            'Content-Type': 'application/json'
        }
        json_data = json.dumps(data)
        response = self.client.post(uri, headers=headers, content_type='application/json', data=json_data)
        return response

    def do_delete(self, uri):
        """Submit an HTTP DELETE request"""
        headers = {
            'Content-Type': 'application/json',
            'X-Edx-Api-Key': str(TEST_API_KEY),
        }
        response = self.client.delete(uri, headers=headers)
        return response

    def _submit_user_scores(self):
        """Submit user scores for modules in the course"""
        # Submit user scores for the first module in the course
        # The looping is a bit wacky here, but it actually does work out correctly
        for j, user in enumerate(self.users):
            # Ensure all database entries in this block record the same timestamps
            # We record each user on a different day across the series to test the aggregations
            submit_time = self.reference_date - timedelta(days=(self.user_count - j), minutes=-30)
            with freeze_time(submit_time):
                module = self.get_module_for_user(user, self.course, self.item)
                self.grade_dict['user_id'] = user.id
                module.system.publish(module, 'grade', self.grade_dict)

                # For the final two users, submit an score for the second module
                if j >= self.user_count - 2:
                    second_module = self.get_module_for_user(user, self.course, self.item2)
                    second_module.system.publish(second_module, 'grade', self.grade_dict)
                    # Add an entry to the gradebook in addition to the scoring -- this is for completions
                    try:
                        sg_entry = StudentGradebook.objects.get(user=user, course_id=self.course.id)
                        sg_entry.grade = 0.9
                        sg_entry.proforma_grade = 0.91
                        sg_entry.save()
                    except StudentGradebook.DoesNotExist:
                        StudentGradebook.objects.create(user=user, course_id=self.course.id, grade=0.9,
                                                        proforma_grade=0.91)

        # Submit scores for the second module for the first five users
        # Pretend the scores were submitted over the course of the final five days
        for j, user in enumerate(self.users[:5]):
            submit_time = self.reference_date - timedelta(days=(5 - j), minutes=-30)
            with freeze_time(submit_time):
                self.grade_dict['user_id'] = user.id
                second_module = self.get_module_for_user(user, self.course, self.item2)
                second_module.system.publish(second_module, 'grade', self.grade_dict)

    def test_courses_data_time_series_metrics_for_first_five_days(self):
        """
        Calculate time series metrics for users in a particular course for first five days.
        """
        # Submit user scores for modules in the course
        self._submit_user_scores()

        # Generate the time series report for the first five days of the set, filtered by organization
        # There should be one time series entry per day for each category, each day having varying counts
        end_date = self.reference_date - timedelta(days=(self.user_count - 4))
        start_date = self.reference_date - timedelta(days=self.user_count)
        date_parameters = {
            'start_date': start_date,
            'end_date': end_date
        }
        course_metrics_uri = '{}/{}/time-series-metrics/?{}&organization={}'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            urlencode(date_parameters),
            self.org_id
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_not_started']), 5)
        total_not_started = sum([not_started[1] for not_started in response.data['users_not_started']])
        self.assertEqual(total_not_started, 110)  # Aggregate total in the first five days (24,23,22,21,20)
        self.assertEqual(len(response.data['users_started']), 5)
        total_started = sum([started[1] for started in response.data['users_started']])
        self.assertEqual(total_started, 5)  # Five users started in the first five days
        self.assertEqual(len(response.data['users_completed']), 5)
        total_completed = sum([completed[1] for completed in response.data['users_completed']])
        self.assertEqual(total_completed, 0)  # Zero users completed in the first five days
        self.assertEqual(len(response.data['modules_completed']), 5)
        total_modules_completed = sum([completed[1] for completed in response.data['modules_completed']])
        self.assertEqual(total_modules_completed, 5)  # Five modules completed in the first five days
        self.assertEqual(len(response.data['active_users']), 5)
        total_active = sum([active[1] for active in response.data['active_users']])
        self.assertEqual(total_active, 4)  # Four active users in the first five days due to how 'active' is defined
        self.assertEqual(len(response.data['users_enrolled']), 5)
        self.assertEqual(response.data['users_enrolled'][0][1], 25)
        total_enrolled = sum([enrolled[1] for enrolled in response.data['users_enrolled']])
        self.assertEqual(total_enrolled, 25)  # Remember, everyone was enrolled on the first day

    def test_courses_data_time_series_metrics_for_final_five_days(self):
        """
        Calculate time series metrics for users in a particular course for final five days.
        """
        # Submit user scores for modules in the course
        self._submit_user_scores()

        # Generate the time series report for the final five days, filtered by organization
        end_date = self.reference_date
        start_date = end_date - relativedelta(days=4)
        date_parameters = {
            'start_date': start_date,
            'end_date': end_date
        }
        course_metrics_uri = '{}/{}/time-series-metrics/?{}&organization={}'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            urlencode(date_parameters),
            self.org_id
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_not_started']), 5)
        total_not_started = sum([not_started[1] for not_started in response.data['users_not_started']])
        self.assertEqual(total_not_started, 6)  # Ticking down the nonstarters -- 3, 2, 1, 0, 0
        self.assertEqual(len(response.data['users_started']), 5)
        total_started = sum([started[1] for started in response.data['users_started']])
        self.assertEqual(total_started, 4)  # Four users started in the final five days
        self.assertEqual(len(response.data['users_completed']), 5)
        total_completed = sum([completed[1] for completed in response.data['users_completed']])
        self.assertEqual(total_completed, 2)  # Two users completed in the final five days (see setup above)
        self.assertEqual(len(response.data['modules_completed']), 5)
        total_modules_completed = sum([completed[1] for completed in response.data['modules_completed']])
        self.assertEqual(total_modules_completed, 10)  # Ten modules completed in the final five days
        self.assertEqual(len(response.data['active_users']), 5)
        total_active = sum([active[1] for active in response.data['active_users']])
        self.assertEqual(total_active, 10)  # Ten active users in the final five days
        self.assertEqual(len(response.data['users_enrolled']), 5)
        self.assertEqual(response.data['users_enrolled'][0][1], 0)
        total_enrolled = sum([enrolled[1] for enrolled in response.data['users_enrolled']])
        self.assertEqual(total_enrolled, 0)  # Remember, everyone was enrolled on the first day, so zero is correct here

    def test_courses_data_time_series_metrics_with_three_weeks_interval(self):
        """
        Calculate time series metrics for users in a particular course with three weeks interval.
        """
        # Submit user scores for modules in the course
        self._submit_user_scores()

        # Change the time interval to three weeks, so we should now see three entries per category
        end_date = self.reference_date
        start_date = end_date - relativedelta(weeks=2)
        date_parameters = {
            'start_date': start_date,
            'end_date': end_date
        }
        course_metrics_uri = '{}/{}/time-series-metrics/?{}&interval=weeks'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            urlencode(date_parameters)
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_not_started']), 3)
        total_not_started = sum([not_started[1] for not_started in response.data['users_not_started']])
        self.assertEqual(total_not_started, 5)
        self.assertEqual(len(response.data['users_started']), 3)
        total_started = sum([started[1] for started in response.data['users_started']])
        self.assertEqual(total_started, 18)
        self.assertEqual(len(response.data['users_completed']), 3)
        total_completed = sum([completed[1] for completed in response.data['users_completed']])
        self.assertEqual(total_completed, 2)
        self.assertEqual(len(response.data['modules_completed']), 3)
        total_modules_completed = sum([completed[1] for completed in response.data['modules_completed']])
        self.assertEqual(total_modules_completed, 25)
        self.assertEqual(len(response.data['active_users']), 3)
        total_active = sum([active[1] for active in response.data['active_users']])
        self.assertEqual(total_active, 23)  # Three weeks x one user per day
        self.assertEqual(len(response.data['users_enrolled']), 3)
        self.assertEqual(response.data['users_enrolled'][0][1], 0)
        total_enrolled = sum([enrolled[1] for enrolled in response.data['users_enrolled']])
        self.assertEqual(total_enrolled, 0)  # No users enrolled in this series

    def test_courses_data_time_series_metrics_with_four_months_interval(self):
        """
        Calculate time series metrics for users in a particular course with four months interval.
        """
        # Submit user scores for modules in the course
        self._submit_user_scores()

        # Change the time interval to four months, so we're back to four entries per category
        end_date = self.reference_date + relativedelta(months=1)
        start_date = end_date - relativedelta(months=3)
        date_parameters = {
            'start_date': start_date,
            'end_date': end_date
        }
        course_metrics_uri = '{}/{}/time-series-metrics/?{}&interval=months'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            urlencode(date_parameters)
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_not_started']), 4)
        total_not_started = sum([not_started[1] for not_started in response.data['users_not_started']])
        self.assertEqual(total_not_started, 20)  # 5 users started in july from 27th to 31st
        self.assertEqual(len(response.data['users_started']), 4)
        total_started = sum([started[1] for started in response.data['users_started']])
        self.assertEqual(total_started, 25)  # All users have started
        self.assertEqual(len(response.data['users_completed']), 4)
        total_completed = sum([completed[1] for completed in response.data['users_completed']])
        self.assertEqual(total_completed, 2)  # Two completions logged
        self.assertEqual(len(response.data['modules_completed']), 4)
        total_modules_completed = sum([completed[1] for completed in response.data['modules_completed']])
        self.assertEqual(total_modules_completed, 32)  # 25 for all + 5 for some + 2 for two
        self.assertEqual(len(response.data['active_users']), 4)
        total_active = sum([active[1] for active in response.data['active_users']])
        self.assertEqual(total_active, 30)  # All users active at some point in this timeframe
        self.assertEqual(response.data['users_enrolled'][1][1], 25)
        total_enrolled = sum([enrolled[1] for enrolled in response.data['users_enrolled']])
        self.assertEqual(total_enrolled, 25)  # All users enrolled in third month of this series

    def test_courses_data_time_series_metrics_after_unenrolling_users(self):
        # Submit user scores for modules in the course
        self._submit_user_scores()

        # Unenroll five users from the course and run the time series report for the final eleven days
        test_uri = self.base_courses_uri + '/' + unicode(self.course.id) + '/users'
        for user in self.users[-5:]:
            unenroll_uri = '{}/{}'.format(test_uri, user.id)
            response = self.do_delete(unenroll_uri)
            self.assertEqual(response.status_code, 204)
        end_date = self.reference_date
        start_date = end_date - relativedelta(days=10)
        date_parameters = {
            'start_date': start_date,
            'end_date': end_date
        }
        course_metrics_uri = '{}/{}/time-series-metrics/?{}&organization={}'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            urlencode(date_parameters),
            self.org_id
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_not_started']), 11)
        total_not_started = sum([not_started[1] for not_started in response.data['users_not_started']])
        self.assertEqual(total_not_started, 10)  # 4,3,2,1, then all zeroes due to the unenrolling
        self.assertEqual(len(response.data['users_started']), 11)
        total_started = sum([started[1] for started in response.data['users_started']])
        self.assertEqual(total_started, 5)  # Five, then nothin
        self.assertEqual(len(response.data['users_completed']), 11)
        total_completed = sum([completed[1] for completed in response.data['users_completed']])
        self.assertEqual(total_completed, 0)  # Only completions were on days 1 and 2
        self.assertEqual(len(response.data['modules_completed']), 11)
        total_modules_completed = sum([completed[1] for completed in response.data['modules_completed']])
        self.assertEqual(total_modules_completed, 10)  # We maintain the module completions after unenrolling
        self.assertEqual(len(response.data['active_users']), 11)
        total_active = sum([active[1] for active in response.data['active_users']])
        self.assertEqual(total_active, 11)

    def test_courses_data_time_series_metrics_user_group_filter(self):
        """
        Test time series metrics for users in a particular course and filter by organizations and group
        """
        # Submit user scores for modules in the course
        self._submit_user_scores()

        # Generate the time series report for the first five days of the set, filtered by organization and group
        # There should be one time series entry per day for each category, each day having varying counts
        end_date = self.reference_date - timedelta(days=(self.user_count - 4))
        start_date = self.reference_date - timedelta(days=self.user_count)
        date_parameters = {
            'start_date': start_date,
            'end_date': end_date
        }
        course_metrics_uri = '{}/{}/time-series-metrics/?{}&organization={}&groups={}'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            urlencode(date_parameters),
            self.org_id,
            self.groups[0].id
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_not_started']), 5)
        total_not_started = sum([not_started[1] for not_started in response.data['users_not_started']])
        self.assertEqual(total_not_started, 56)  # Aggregate total in the first five days in group 1 (12,12,11,11,10)
        self.assertEqual(len(response.data['users_started']), 5)
        total_started = sum([started[1] for started in response.data['users_started']])
        self.assertEqual(total_started, 3)  # Five users started in the first five days three in group 1
        self.assertEqual(len(response.data['users_completed']), 5)
        total_completed = sum([completed[1] for completed in response.data['users_completed']])
        self.assertEqual(total_completed, 0)  # Zero users completed in the first five days
        self.assertEqual(len(response.data['modules_completed']), 5)
        total_modules_completed = sum([completed[1] for completed in response.data['modules_completed']])
        # Five modules completed in the first five days, 3 users in group 1
        self.assertEqual(total_modules_completed, 3)
        self.assertEqual(len(response.data['active_users']), 5)
        total_active = sum([active[1] for active in response.data['active_users']])
        # Four active users in the first five days due to how 'active' is defined, 2 users in group 1
        self.assertEqual(total_active, 2)
        self.assertEqual(len(response.data['users_enrolled']), 5)
        self.assertEqual(response.data['users_enrolled'][0][1], 13)
        total_enrolled = sum([enrolled[1] for enrolled in response.data['users_enrolled']])
        self.assertEqual(total_enrolled, 13)  # Everyone was enrolled on the first day, 13 users in group 1

    def test_courses_data_time_series_metrics_user_multiple_group_filter(self):
        """
        Calculate time series metrics for users in a particular course.
        """
        # Submit user scores for modules in the course
        self._submit_user_scores()

        # Generate the time series report for the first five days of the set, filtered by organization & multiple groups
        # There should be one time series entry per day for each category, each day having varying counts
        end_date = self.reference_date - timedelta(days=(self.user_count - 4))
        start_date = self.reference_date - timedelta(days=self.user_count)
        date_parameters = {
            'start_date': start_date,
            'end_date': end_date
        }
        group_ids = ','.join([str(group.id) for group in self.groups])
        course_metrics_uri = '{}/{}/time-series-metrics/?{}&organization={}&groups={}'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            urlencode(date_parameters),
            self.org_id,
            group_ids
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_not_started']), 5)
        total_not_started = sum([not_started[1] for not_started in response.data['users_not_started']])
        self.assertEqual(total_not_started, 110)  # Aggregate total in the first five days (24,23,22,21,20)
        self.assertEqual(len(response.data['users_started']), 5)
        total_started = sum([started[1] for started in response.data['users_started']])
        self.assertEqual(total_started, 5)  # Five users started in the first five days
        self.assertEqual(len(response.data['users_completed']), 5)
        total_completed = sum([completed[1] for completed in response.data['users_completed']])
        self.assertEqual(total_completed, 0)  # Zero users completed in the first five days
        self.assertEqual(len(response.data['modules_completed']), 5)
        total_modules_completed = sum([completed[1] for completed in response.data['modules_completed']])
        self.assertEqual(total_modules_completed, 5)  # Five modules completed in the first five days
        self.assertEqual(len(response.data['active_users']), 5)
        total_active = sum([active[1] for active in response.data['active_users']])
        self.assertEqual(total_active, 4)  # Four active users in the first five days due to how 'active' is defined
        self.assertEqual(len(response.data['users_enrolled']), 5)
        self.assertEqual(response.data['users_enrolled'][0][1], 25)
        total_enrolled = sum([enrolled[1] for enrolled in response.data['users_enrolled']])
        self.assertEqual(total_enrolled, 25)  # Remember, everyone was enrolled on the first day

    def test_courses_data_time_series_metrics_without_end_date(self):
        # Missing end date should raise an error
        start_date = self.reference_date - relativedelta(days=10)

        course_metrics_uri = '{}/{}/time-series-metrics/?start_date={}'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            start_date
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 400)

    def test_courses_data_time_series_metrics_with_invalid_interval(self):
        # Unsupported interval should raise an error
        end_date = self.reference_date
        start_date = end_date - relativedelta(days=10)

        course_metrics_uri = '{}/{}/time-series-metrics/?start_date={}&end_date={}&interval=hours'.format(
            self.base_courses_uri,
            unicode(self.course.id),
            start_date,
            end_date
        )
        response = self.do_get(course_metrics_uri)
        self.assertEqual(response.status_code, 400)
