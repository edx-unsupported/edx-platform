"""
Courses API URI specification
The order of the URIs really matters here, due to the slash characters present in the identifiers
"""
from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from api_manager.courses import views as courses_views

urlpatterns = patterns(
    '',
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/content/(?P<content_id>[a-zA-Z0-9_+\/:-]+)/groups/(?P<group_id>[0-9]+)$', courses_views.CourseContentGroupsDetail.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/content/(?P<content_id>[a-zA-Z0-9_+\/:-]+)/groups/*$', courses_views.CourseContentGroupsList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/content/(?P<content_id>[a-zA-Z0-9_+\/:-]+)/children/*$', courses_views.CourseContentList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/content/(?P<content_id>[a-zA-Z0-9_+\/:-]+)/users/*$', courses_views.CourseContentUsersList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/content/(?P<content_id>[a-zA-Z0-9_+\/:-]+)$', courses_views.CourseContentDetail.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/content/*$', courses_views.CourseContentList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/groups/(?P<group_id>[0-9]+)$', courses_views.CoursesGroupsDetail.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/groups/*$', courses_views.CoursesGroupsList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/overview/*$', courses_views.CoursesOverview.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/static_tabs/(?P<tab_id>[a-zA-Z0-9_+\/:-]+)$', courses_views.CoursesStaticTabsDetail.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/static_tabs/*$', courses_views.CoursesStaticTabsList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/completions/*$', courses_views.CourseModuleCompletionList.as_view(), name='completion-list'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/projects/*$', courses_views.CoursesProjectList.as_view(), name='courseproject-list'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/metrics/*$', courses_views.CoursesMetrics.as_view(), name='course-metrics'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/time-series-metrics/*$', courses_views.CoursesTimeSeriesMetrics.as_view(), name='course-time-series-metrics'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/metrics/cities/$', courses_views.CoursesMetricsCities.as_view(), name='courses-cities-metrics'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/metrics/completions/leaders/*$', courses_views.CoursesMetricsCompletionsLeadersList.as_view(), name='course-metrics-completions-leaders'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/metrics/grades/*$', courses_views.CoursesMetricsGradesList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/metrics/grades/leaders/*$', courses_views.CoursesMetricsGradesLeadersList.as_view(), name='course-metrics-grades-leaders'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/metrics/social/$', courses_views.CoursesMetricsSocial.as_view(), name='courses-social-metrics'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/roles/(?P<role>[a-z_]+)/users/(?P<user_id>[0-9]+)*$', courses_views.CoursesRolesUsersDetail.as_view(), name='courses-roles-users-detail'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/roles/*$', courses_views.CoursesRolesList.as_view(), name='courses-roles-list'),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/updates/*$', courses_views.CoursesUpdates.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/users/(?P<user_id>[0-9]+)$', courses_views.CoursesUsersDetail.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/users/*$', courses_views.CoursesUsersList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)/workgroups/*$', courses_views.CoursesWorkgroupsList.as_view()),
    url(r'^(?P<course_id>[a-zA-Z0-9_+\/:-]+)$', courses_views.CoursesDetail.as_view()),
    url(r'/*$^', courses_views.CoursesList.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
