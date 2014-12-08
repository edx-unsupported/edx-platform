""" Users API URI specification """
from django.conf import settings
from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from api_manager.users import views as users_views

COURSE_ID_PATTERN = settings.COURSE_ID_PATTERN

urlpatterns = patterns(
    '',
    url(r'^metrics/cities/$', users_views.UsersMetricsCitiesList.as_view(), name='apimgr-users-metrics-cities-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/{}/metrics/social/$'.format(COURSE_ID_PATTERN), users_views.UsersSocialMetrics.as_view(), name='users-social-metrics'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/{}$'.format(COURSE_ID_PATTERN), users_views.UsersCoursesDetail.as_view(), name='users-courses-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/*$', users_views.UsersCoursesList.as_view(), name='users-courses-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/groups/*$', users_views.UsersGroupsList.as_view(), name='users-groups-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/groups/(?P<group_id>[0-9]+)$', users_views.UsersGroupsDetail.as_view(), name='users-groups-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/preferences$', users_views.UsersPreferences.as_view(), name='users-preferences-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/preferences/(?P<preference_id>[a-zA-Z0-9_]+)$', users_views.UsersPreferencesDetail.as_view(), name='users-preferences-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/roles/(?P<role>[a-z_]+)/courses/{}$'.format(COURSE_ID_PATTERN), users_views.UsersRolesCoursesDetail.as_view(), name='users-roles-courses-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/roles/*$', users_views.UsersRolesList.as_view(), name='users-roles-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)$', users_views.UsersDetail.as_view(), name='apimgr-users-detail'),
    url(r'/*$^', users_views.UsersList.as_view(), name='apimgr-users-list'),
)

if settings.FEATURES.get('GRADEBOOK_APP', False):
    urlpatterns += (
        url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/{}/grades$'.format(COURSE_ID_PATTERN), users_views.UsersCoursesGradesDetail.as_view(), name='users-courses-grades-detail'),
    )

if settings.FEATURES.get('ORGANIZATIONS_APP', False):
    urlpatterns += (
        url(r'^(?P<user_id>[a-zA-Z0-9]+)/organizations/$', users_views.UsersOrganizationsList.as_view(), name='users-organizations-list'),
    )

if settings.FEATURES.get('PROGRESS_APP', False):
    urlpatterns += (
        url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/{}/completions/$'.format(COURSE_ID_PATTERN), users_views.UsersCoursesCompletionsList.as_view(), name='users-courses-completions-list'),
    )

if settings.FEATURES.get('PROJECTS_APP', False):
    urlpatterns += (
        url(r'^(?P<user_id>[a-zA-Z0-9]+)/workgroups/$', users_views.UsersWorkgroupsList.as_view(), name='users-workgroups-list'),
    )

urlpatterns = format_suffix_patterns(urlpatterns)
