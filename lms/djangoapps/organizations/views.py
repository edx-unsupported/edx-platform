# pylint: disable=C0103

""" ORGANIZATIONS API VIEWS """
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, F, Count

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api_manager.courseware_access import get_course_key, get_aggregate_exclusion_user_ids
from api_manager.models import GroupProfile
from api_manager.users.serializers import UserSerializer
from api_manager.utils import str2bool
from student.models import CourseEnrollment

if settings.FEATURES.get('GRADEBOOK_APP', False):
    from gradebook.models import StudentGradebook

from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationsViewSet(viewsets.ModelViewSet):
    """
    Django Rest Framework ViewSet for the Organization model.
    """
    serializer_class = OrganizationSerializer
    model = Organization

    @action(methods=['get', ])
    def metrics(self, request, pk):
        """
        Provide statistical information for the specified Organization
        """
        if not settings.FEATURES.get('GRADEBOOK_APP', False):
            return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
        response_data = {}
        grade_avg = 0
        grade_complete_match_range = getattr(settings, 'GRADEBOOK_GRADE_COMPLETE_PROFORMA_MATCH_RANGE', 0.01)
        org_user_grades = StudentGradebook.objects.filter(user__organizations=pk, user__is_active=True,
                                                          user__courseenrollment__is_active=True)
        courses_filter = request.QUERY_PARAMS.get('courses', None)
        courses = []
        if courses_filter:
            upper_bound = getattr(settings, 'API_LOOKUP_UPPER_BOUND', 100)
            courses_filter = courses_filter.split(",")[:upper_bound]
            for course_string in courses_filter:
                courses.append(get_course_key(course_string))
            org_user_grades = org_user_grades.filter(course_id__in=courses,
                                                     user__courseenrollment__course_id__in=courses)

        users_grade_sum = org_user_grades.aggregate(Sum('grade'))
        if users_grade_sum['grade__sum']:
            exclude_users = set()
            for course_key in courses:
                exclude_users.union(get_aggregate_exclusion_user_ids(course_key))
            users_enrolled_qs = CourseEnrollment.objects.filter(user__is_active=True, is_active=True,
                                                                user__organizations=pk)\
                .exclude(user_id__in=exclude_users)
            if courses:
                users_enrolled_qs = users_enrolled_qs.filter(course_id__in=courses)
            users_enrolled = users_enrolled_qs.aggregate(Count('user', distinct=True))
            total_users = users_enrolled['user__count']
            if total_users:
                grade_avg = float('{0:.3f}'.format(float(users_grade_sum['grade__sum']) / total_users))
        response_data['users_grade_average'] = grade_avg

        users_grade_complete_count = org_user_grades\
            .filter(proforma_grade__lte=F('grade') + grade_complete_match_range, proforma_grade__gt=0).count()
        response_data['users_grade_complete_count'] = users_grade_complete_count

        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['get', 'post'])
    def users(self, request, pk):
        """
        Add a User to an Organization
        """
        if request.method == 'GET':
            include_course_counts = request.QUERY_PARAMS.get('include_course_counts', None)
            users = User.objects.filter(organizations=pk)
            response_data = []
            if users:
                for user in users:
                    serializer = UserSerializer(user)
                    user_data = serializer.data
                    if str2bool(include_course_counts):
                        enrollments = CourseEnrollment.enrollments_for_user(user).count()
                        user_data['course_count'] = enrollments
                    response_data.append(user_data)
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            user_id = request.DATA.get('id')
            try:
                user = User.objects.get(id=user_id)
            except ObjectDoesNotExist:
                message = 'User {} does not exist'.format(user_id)
                return Response({"detail": message}, status.HTTP_400_BAD_REQUEST)
            organization = self.get_object()
            organization.users.add(user)
            organization.save()
            return Response({}, status=status.HTTP_201_CREATED)

    @action(methods=['get', 'post'])
    def groups(self, request, pk):
        """
        Add a Group to a organization or retrieve list of groups in organization
        """
        if request.method == 'GET':
            group_type = request.QUERY_PARAMS.get('type', None)
            groups = Group.objects.filter(organizations=pk)
            if group_type:
                groups = groups.filter(groupprofile__group_type=group_type)
            response_data = []
            if groups:
                for group in groups:
                    group_data = {}
                    group_data['id'] = group.id
                    group_data['name'] = group.name
                    group_data['type'] = None
                    group_data['data'] = None
                    group_profile = GroupProfile.objects.filter(group_id=group.id)
                    if group_profile:
                        group_data['name'] = group_profile[0].name
                        group_data['type'] = group_profile[0].group_type
                        group_data['data'] = group_profile[0].data
                    response_data.append(group_data)  # pylint: disable=E1101
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            group_id = request.DATA.get('id')
            try:
                group = Group.objects.get(id=group_id)
            except ObjectDoesNotExist:
                message = 'Group {} does not exist'.format(group_id)
                return Response({"detail": message}, status.HTTP_400_BAD_REQUEST)
            organization = self.get_object()
            organization.groups.add(group)
            organization.save()
            return Response({}, status=status.HTTP_201_CREATED)
