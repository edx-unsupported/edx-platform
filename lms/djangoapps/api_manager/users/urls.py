""" Users API URI specification """
from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from api_manager.users import views as users_views

urlpatterns = patterns(
    '',
    url(r'^metrics/cities/$', users_views.UsersMetricsCitiesList.as_view(), name='apimgr-users-metrics-cities-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/(?P<course_id>[^/]+/[^/]+/[^/]+)/grades$', users_views.UsersCoursesGradesDetail.as_view(), name='users-courses-grades-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/(?P<course_id>[^/]+/[^/]+/[^/]+)/metrics/social/$', users_views.UsersSocialMetrics.as_view(), name='users-social-metrics'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/(?P<course_id>[^/]+/[^/]+/[^/]+)/completions/$', users_views.UsersCoursesCompletionsList.as_view(), name='users-courses-completions-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/(?P<course_id>[^/]+/[^/]+/[^/]+)$', users_views.UsersCoursesDetail.as_view(), name='users-courses-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/(?P<course_id>[a-zA-Z0-9_+\/:]+)/grades$', users_views.UsersCoursesGradesDetail.as_view(), name='users-courses-grades-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/(?P<course_id>[a-zA-Z0-9_+\/:]+)/metrics/social/$', users_views.UsersSocialMetrics.as_view(), name='users-social-metrics'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/(?P<course_id>[a-zA-Z0-9_+\/:]+)/completions/$', users_views.UsersCoursesCompletionsList.as_view(), name='users-courses-completions-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/(?P<course_id>[a-zA-Z0-9_+\/:]+)$', users_views.UsersCoursesDetail.as_view(), name='users-courses-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/courses/*$', users_views.UsersCoursesList.as_view(), name='users-courses-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/groups/*$', users_views.UsersGroupsList.as_view(), name='users-groups-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/groups/(?P<group_id>[0-9]+)$', users_views.UsersGroupsDetail.as_view(), name='users-groups-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/preferences$', users_views.UsersPreferences.as_view(), name='users-preferences-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/preferences/(?P<preference_id>[a-zA-Z0-9_]+)$', users_views.UsersPreferencesDetail.as_view(), name='users-preferences-detail'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/organizations/$', users_views.UsersOrganizationsList.as_view(), name='users-organizations-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)/workgroups/$', users_views.UsersWorkgroupsList.as_view(), name='users-workgroups-list'),
    url(r'^(?P<user_id>[a-zA-Z0-9]+)$', users_views.UsersDetail.as_view(), name='apimgr-users-detail'),
    url(r'/*$^', users_views.UsersList.as_view(), name='apimgr-users-list'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
