# pylint: disable=E1103

"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/api_manager/tests/test_group_views.py]
"""
import simplejson as json
import unittest
import uuid
from random import randint

from django.core.cache import cache
from django.test import TestCase, Client
from django.test.utils import override_settings

from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory

from .content import TEST_COURSE_OVERVIEW_CONTENT, TEST_COURSE_UPDATES_CONTENT
from .content import TEST_STATIC_TAB1_CONTENT, TEST_STATIC_TAB2_CONTENT

TEST_API_KEY = str(uuid.uuid4())


class SecureClient(Client):
    """ Django test client using a "secure" connection. """
    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({'SERVER_PORT': 443, 'wsgi.url_scheme': 'https'})
        super(SecureClient, self).__init__(*args, **kwargs)


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
@override_settings(EDX_API_KEY=TEST_API_KEY)
class CoursesApiTests(TestCase):
    """ Test suite for Courses API views """

    def setUp(self):
        self.maxDiff = 3000
        self.test_server_prefix = 'https://testserver'
        self.base_courses_uri = '/api/courses'
        self.base_groups_uri = '/api/groups'
        self.test_group_name = 'Alpha Group'

        self.course = CourseFactory.create()
        self.test_data = '<html>{}</html>'.format(str(uuid.uuid4()))

        self.chapter = ItemFactory.create(
            category="chapter",
            parent_location=self.course.location,
            data=self.test_data,
            display_name="Overview"
        )

        self.module = ItemFactory.create(
            category="videosequence",
            parent_location=self.chapter.location,
            data=self.test_data,
            display_name="Video_Sequence"
        )

        self.submodule = ItemFactory.create(
            category="video",
            parent_location=self.module.location,
            data=self.test_data,
            display_name="Video_Resources"
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
            display_name="syllabus"
        )

        self.static_tab2 = ItemFactory.create(
            category="static_tab",
            parent_location=self.course.location,
            data=TEST_STATIC_TAB2_CONTENT,
            display_name="readings"
        )

        self.test_course_id = self.course.id
        self.test_bogus_course_id = 'foo/bar/baz'
        self.test_course_name = self.course.display_name
        self.test_course_number = self.course.number
        self.test_course_org = self.course.org
        self.test_chapter_id = self.chapter.id
        self.test_module_id = self.module.id
        self.test_submodule_id = self.submodule.id
        self.base_modules_uri = '/api/courses/' + self.test_course_id + '/modules'
        self.base_chapters_uri = self.base_modules_uri + '?type=chapter'

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
        for item in items:
            if item['class'] == class_name:
                return item
        return None

    def test_courses_list_get(self):
        test_uri = self.base_courses_uri
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        matched_course = False
        for course in response.data:
            if matched_course is False and course['id'] == self.test_course_id:
                self.assertEqual(course['name'], self.test_course_name)
                self.assertEqual(course['number'], self.test_course_number)
                self.assertEqual(course['org'], self.test_course_org)
                confirm_uri = self.test_server_prefix + test_uri + '/' + course['id']
                self.assertEqual(course['uri'], confirm_uri)
                matched_course = True
        self.assertTrue(matched_course)

    def test_courses_detail_get(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], self.test_course_id)
        self.assertEqual(response.data['name'], self.test_course_name)
        self.assertEqual(response.data['number'], self.test_course_number)
        self.assertEqual(response.data['org'], self.test_course_org)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)

    def test_courses_detail_get_with_submodules(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '?depth=100'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], self.test_course_id)
        self.assertEqual(response.data['name'], self.test_course_name)
        self.assertEqual(response.data['number'], self.test_course_number)
        self.assertEqual(response.data['org'], self.test_course_org)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertGreater(len(response.data['modules']), 0)

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
        self.assertEqual(len(response.data['modules']), 1)

        chapter = response.data['modules'][0]
        self.assertEqual(chapter['category'], 'chapter')
        self.assertEqual(chapter['name'], 'Overview')
        self.assertEqual(len(chapter['modules']), 1)

        sequence = chapter['modules'][0]
        self.assertEqual(sequence['category'], 'videosequence')
        self.assertEqual(sequence['name'], 'Video_Sequence')
        self.assertNotIn('modules', sequence)

    def test_courses_tree_get_root(self):
        # query the course tree to quickly get naviation information
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '?depth=0'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['category'], 'course')
        self.assertEqual(response.data['name'], self.course.display_name)
        self.assertNotIn('modules', response.data)

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
                confirm_uri = self.test_server_prefix + self.base_modules_uri + '/' + chapter['id']
                self.assertEqual(chapter['uri'], confirm_uri)
                matched_chapter = True
        self.assertTrue(matched_chapter)

    def test_chapter_detail_get(self):
        test_uri = self.base_modules_uri + '/' + self.test_chapter_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['id']), 0)
        self.assertEqual(response.data['id'], self.test_chapter_id)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertGreater(len(response.data['modules']), 0)

    def test_modules_list_get(self):
        test_uri = self.base_modules_uri + '/' + self.test_module_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        matched_submodule = False
        for submodule in response.data['modules']:
            if matched_submodule is False and submodule['id'] == self.test_submodule_id:
                self.assertIsNotNone(submodule['uri'])
                self.assertGreater(len(submodule['uri']), 0)
                confirm_uri = self.test_server_prefix + self.base_modules_uri + '/' + submodule['id']
                self.assertEqual(submodule['uri'], confirm_uri)
                matched_submodule = True
        self.assertTrue(matched_submodule)

    def test_modules_detail_get(self):
        test_uri = self.base_modules_uri + '/' + self.test_module_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], self.test_module_id)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertGreater(len(response.data['modules']), 0)

    def test_modules_detail_get_course(self):
        test_uri = self.base_modules_uri + '/' + self.test_course_id
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['id'], self.test_course_id)
        confirm_uri = self.test_server_prefix + self.base_courses_uri + '/' + self.test_course_id
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertGreater(len(response.data['modules']), 0)

    def test_modules_detail_get_notfound(self):
        test_uri = self.base_modules_uri + '/' + '2p38fp2hjfp9283'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_modules_list_get_filtered_submodules_for_module(self):
        test_uri = self.base_modules_uri + '/' + self.test_module_id + '/submodules?type=video'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        matched_submodule = False
        for submodule in response.data:
            if matched_submodule is False and submodule['id'] == self.test_submodule_id:
                confirm_uri = self.test_server_prefix + self.base_modules_uri + '/' + submodule['id']
                self.assertEqual(submodule['uri'], confirm_uri)
                matched_submodule = True
        self.assertTrue(matched_submodule)

    def test_modules_list_get_notfound(self):
        test_uri = self.base_modules_uri + '/2p38fp2hjfp9283/submodules?type=video'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_groups_list_post(self):
        data = {'name': self.test_group_name}
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

    def test_courses_groups_list_post_duplicate(self):
        data = {'name': self.test_group_name}
        response = self.do_post(self.base_groups_uri, data)
        group_id = response.data['id']
        test_uri = '{}/{}/groups'.format(self.base_courses_uri, self.test_course_id)
        data = {'group_id': group_id}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 409)

    def test_courses_groups_list_post_invalid_resources(self):
        test_uri = self.base_courses_uri + '/1239/87/8976/groups'
        data = {'group_id': "98723896"}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 404)

    def test_courses_groups_detail_get(self):
        data = {'name': self.test_group_name}
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
        course_id = 'asd/fas/vcsadfaf'
        group_id = '12343'
        test_uri = '{}/{}/groups/{}'.format(self.base_courses_uri, course_id, group_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertEqual(response.data['course_id'], course_id)
        self.assertEqual(response.data['group_id'], group_id)

    def test_courses_groups_detail_delete(self):
        data = {'name': self.test_group_name}
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
        data = {'name': self.test_group_name}
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

    def test_courses_overview_get_parsed(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/overview?parse=true'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        sections = response.data['sections']
        self.assertEqual(len(sections), 4)
        self.assertIsNotNone(self._find_item_by_class(sections, 'about'))
        self.assertIsNotNone(self._find_item_by_class(sections, 'prerequisites'))
        self.assertIsNotNone(self._find_item_by_class(sections, 'course-staff'))
        self.assertIsNotNone(self._find_item_by_class(sections, 'faq'))

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

    def test_courses_overview_get_invalid_course(self):
        #try a bogus course_id to test failure case
        test_uri = '{}/{}/overview'.format(self.base_courses_uri, self.test_bogus_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_overview_get_invalid_content(self):
        #try a bogus course_id to test failure case
        test_course = CourseFactory.create()
        test_uri = '{}/{}/overview'.format(self.base_courses_uri, test_course.id)
        test_updates = ItemFactory.create(
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
        test_course_data = '<html>{}</html>'.format(str(uuid.uuid4()))
        test_updates = ItemFactory.create(
            category="course_info",
            parent_location=test_course.location,
            data='',
            display_name="updates"
        )
        test_uri = '{}/{}/updates'.format(self.base_courses_uri, test_course.id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_static_tab_list_get(self):
        test_uri = '{}/{}/static_tabs'.format(self.base_courses_uri, self.test_course_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        tabs = response.data['tabs']
        self.assertEqual(len(tabs), 2)
        self.assertEqual(tabs[0]['name'], u'syllabus')
        self.assertEqual(tabs[0]['id'], u'syllabus')
        self.assertEqual(tabs[1]['name'], u'readings')
        self.assertEqual(tabs[1]['id'], u'readings')

        # now try when we get the details on the tabs
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs?detail=true'
        response = self.do_get(test_uri)

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        tabs = response.data['tabs']
        self.assertEqual(tabs[0]['name'], u'syllabus')
        self.assertEqual(tabs[0]['id'], u'syllabus')
        self.assertEqual(tabs[0]['content'], self.static_tab1.data)
        self.assertEqual(tabs[1]['name'], u'readings')
        self.assertEqual(tabs[1]['id'], u'readings')
        self.assertEqual(tabs[1]['content'], self.static_tab2.data)

    def test_static_tab_list_get_invalid_course(self):
        #try a bogus course_id to test failure case
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id + '/static_tabs'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_static_tab_detail_get(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs/syllabus'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        tab = response.data
        self.assertEqual(tab['name'], u'syllabus')
        self.assertEqual(tab['id'], u'syllabus')
        self.assertEqual(tab['content'], self.static_tab1.data)

        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/static_tabs/readings'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        tab = response.data
        self.assertEqual(tab['name'], u'readings')
        self.assertEqual(tab['id'], u'readings')
        self.assertEqual(tab['content'], self.static_tab2.data)

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
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
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
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
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
        test_user_uri = '/api/users'
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
        test_user_uri = '/api/users'
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

    def test_courses_users_detail_get(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users'
        test_user_uri = '/api/users'
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
        self.assertGreater(len(response.data), 0)

    def test_courses_users_detail_get_invalid_course(self):
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id + '/users/213432'
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
        test_user_uri = '/api/users'
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
        test_uri = self.base_courses_uri + '/' + self.test_bogus_course_id + '/users/213432'
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_courses_users_detail_delete_invalid_user(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/users/213432'
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)
