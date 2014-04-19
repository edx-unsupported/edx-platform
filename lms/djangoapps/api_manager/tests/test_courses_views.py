# pylint: disable=E1103

"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/api_manager/tests/test_group_views.py]
"""
import uuid

from textwrap import dedent

from django.core.cache import cache
from django.test import TestCase, Client
from django.test.utils import override_settings

from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory


TEST_API_KEY = str(uuid.uuid4())

TEST_COURSE_OVERVIEW_CONTENT = dedent("""
        <section class="about">
          <h2>About This Course</h2>
          <p>Include your long course description here. The long course description should contain 150-400 words.</p>

          <p>This is paragraph 2 of the long course description. Add more paragraphs as needed. Make sure to enclose them in paragraph tags.</p>
        </section>

        <section class="prerequisites">
          <h2>Prerequisites</h2>
          <p>Add information about course prerequisites here.</p>
        </section>

        <section class="course-staff">
          <h2>Course Staff</h2>
          <article class="teacher">
            <div class="teacher-image">
              <img src="/images/pl-faculty.png" align="left" style="margin:0 20 px 0" alt="Course Staff Image #1">
            </div>

            <h3>Staff Member #1</h3>
            <p>Biography of instructor/staff member #1</p>
          </article>

          <article class="teacher">
            <div class="teacher-image">
              <img src="/images/pl-faculty.png" align="left" style="margin:0 20 px 0" alt="Course Staff Image #2">
            </div>

            <h3>Staff Member #2</h3>
            <p>Biography of instructor/staff member #2</p>
          </article>
        </section>

        <section class="faq">
            <p>Some text here</p>
        </section>
       """)


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

        self.test_course_id = self.course.id
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
        print "GET: " + uri
        response = self.client.get(uri, headers=headers)
        return response

    def test_course_list_get(self):
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

    def test_course_detail_get(self):
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
        self.assertGreater(len(response.data['modules']), 0)

    def test_course_detail_get_notfound(self):
        test_uri = self.base_courses_uri + '/' + 'p29038cvp9hjwefion'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

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

    def test_get_course_overview_unparsed(self):
        test_uri = self.base_courses_uri + '/' + self.test_course_id + '/overview'

        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['overview_html'], self.overview.data)

    def _find_item_by_class(self, items, class_name):
        for item in items:
            if item['class'] == class_name:
                return item
        return None

    def test_get_course_overview_parsed(self):
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
        teachers = course_staff['articles']
        self.assertEqual(len(teachers), 2)
        self.assertEqual(teachers[0]['name'], "Staff Member #1")
        self.assertEqual(teachers[0]['image_src'], "/images/pl-faculty.png")
        self.assertIn("<p>Biography of instructor/staff member #1</p>", teachers[0]['bio'])
        self.assertEqual(teachers[1]['name'], "Staff Member #2")
        self.assertEqual(teachers[1]['image_src'], "/images/pl-faculty.png")
        self.assertIn("<p>Biography of instructor/staff member #2</p>", teachers[1]['bio'])

        about = self._find_item_by_class(sections, 'about')
        self.assertGreater(len(about['body']), 0)
        prerequisites = self._find_item_by_class(sections, 'prerequisites')
        self.assertGreater(len(prerequisites['body']), 0)
        faq = self._find_item_by_class(sections, 'faq')
        self.assertGreater(len(faq['body']), 0)
