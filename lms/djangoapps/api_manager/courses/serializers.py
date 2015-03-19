""" Django REST Framework Serializers """

from api_manager.models import CourseModuleCompletion
from rest_framework import serializers


class CourseModuleCompletionSerializer(serializers.ModelSerializer):
    """ Serializer for CourseModuleCompletion model interactions """
    user_id = serializers.Field(source='user.id')

    class Meta:
        """ Serializer/field specification """
        model = CourseModuleCompletion
        fields = ('id', 'user_id', 'course_id', 'content_id', 'created', 'modified')
        read_only = ('id', 'created')


class GradeSerializer(serializers.Serializer):
    """ Serializer for model interactions """
    grade = serializers.Field()


class CourseLeadersSerializer(serializers.Serializer):
    """ Serializer for course leaderboard """
    id = serializers.IntegerField(source='student__id')
    username = serializers.CharField(source='student__username')
    title = serializers.CharField(source='student__profile__title')
    avatar_url = serializers.CharField(source='student__profile__avatar_url')
    points_scored = serializers.IntegerField()
