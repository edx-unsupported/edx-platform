# pylint: disable=E1103

"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/projects/tests/test_projects.py]
"""
import json
import uuid

from django.core.cache import cache
from django.test import TestCase, Client
from django.test.utils import override_settings

from projects.models import Workgroup

TEST_API_KEY = str(uuid.uuid4())


class SecureClient(Client):

    """ Django test client using a "secure" connection. """

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({'SERVER_PORT': 443, 'wsgi.url_scheme': 'https'})
        super(SecureClient, self).__init__(*args, **kwargs)


@override_settings(EDX_API_KEY=TEST_API_KEY)
class ProjectsApiTests(TestCase):

    """ Test suite for Users API views """

    def setUp(self):
        self.test_server_prefix = 'https://testserver'
        self.test_projects_uri = '/api/projects/'
        self.test_project_name = str(uuid.uuid4())

        self.test_course_id = 'edx/demo/course'
        self.test_bogus_course_id = 'foo/bar/baz'
        self.test_course_content_id = "i4x://blah"
        self.test_bogus_course_content_id = "14x://foo/bar/baz"

        self.test_workgroup = Workgroup.objects.create(
            name="Test Workgroup",
        )

        self.client = SecureClient()
        cache.clear()

    def do_post(self, uri, data):
        """Submit an HTTP POST request"""
        headers = {
            'X-Edx-Api-Key': str(TEST_API_KEY),
        }
        json_data = json.dumps(data)

        response = self.client.post(
            uri, headers=headers, content_type='application/json', data=json_data)
        return response

    def do_get(self, uri):
        """Submit an HTTP GET request"""
        headers = {
            'Content-Type': 'application/json',
            'X-Edx-Api-Key': str(TEST_API_KEY),
        }
        response = self.client.get(uri, headers=headers)
        return response

    def do_delete(self, uri):
        """Submit an HTTP DELETE request"""
        headers = {
            'Content-Type': 'application/json',
            'X-Edx-Api-Key': str(TEST_API_KEY),
        }
        response = self.client.delete(uri, headers=headers)
        return response

    def test_projects_list_post(self):
        data = {
            'name': self.test_project_name,
            'course_id': self.test_course_id,
            'content_id': self.test_course_content_id
        }
        response = self.do_post(self.test_projects_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(response.data['id'], 0)
        confirm_uri = '{}{}{}/'.format(
            self.test_server_prefix,
            self.test_projects_uri,
            str(response.data['id'])
        )
        self.assertEqual(response.data['url'], confirm_uri)
        self.assertGreater(response.data['id'], 0)
        self.assertEqual(response.data['course_id'], self.test_course_id)
        self.assertEqual(response.data['content_id'], self.test_course_content_id)
        self.assertIsNotNone(response.data['workgroups'])
        self.assertIsNotNone(response.data['created'])
        self.assertIsNotNone(response.data['modified'])

    def test_projects_detail_get(self):
        data = {
            'name': self.test_project_name,
            'course_id': self.test_course_id,
            'content_id': self.test_course_content_id
        }
        response = self.do_post(self.test_projects_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = '{}{}/'.format(self.test_projects_uri, str(response.data['id']))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        confirm_uri = self.test_server_prefix + test_uri
        self.assertEqual(response.data['url'], confirm_uri)
        self.assertGreater(response.data['id'], 0)
        self.assertEqual(response.data['course_id'], self.test_course_id)
        self.assertEqual(response.data['content_id'], self.test_course_content_id)
        self.assertIsNotNone(response.data['workgroups'])
        self.assertIsNotNone(response.data['created'])
        self.assertIsNotNone(response.data['modified'])

    def test_projects_workgroups_post(self):
        data = {
            'name': self.test_project_name,
            'course_id': self.test_course_id,
            'content_id': self.test_course_content_id
        }
        response = self.do_post(self.test_projects_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = '{}{}/'.format(self.test_projects_uri, str(response.data['id']))
        workgroups_uri = '{}workgroups/'.format(test_uri)
        data = {"id": self.test_workgroup.id}
        response = self.do_post(workgroups_uri, data)
        self.assertEqual(response.status_code, 201)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['workgroups'][0]['id'], self.test_workgroup.id)

    def test_projects_workgroups_post_invalid_workgroup(self):
        data = {
            'name': self.test_project_name,
            'course_id': self.test_course_id,
            'content_id': self.test_course_content_id
        }
        response = self.do_post(self.test_projects_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = '{}{}/'.format(self.test_projects_uri, str(response.data['id']))
        workgroups_uri = '{}workgroups/'.format(test_uri)
        data = {
            'id': 123456,
        }
        response = self.do_post(workgroups_uri, data)
        self.assertEqual(response.status_code, 400)

    def test_projects_detail_get_undefined(self):
        test_uri = '/api/projects/123456789/'
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_projects_detail_delete(self):
        data = {
            'name': self.test_project_name,
            'course_id': self.test_course_id,
            'content_id': self.test_course_content_id
        }
        response = self.do_post(self.test_projects_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = '{}{}/'.format(self.test_projects_uri, str(response.data['id']))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)
