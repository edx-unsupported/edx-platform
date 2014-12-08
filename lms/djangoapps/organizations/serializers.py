""" Django REST Framework Serializers """

from django.conf import settings

from rest_framework import serializers

from organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """ Serializer for Organization model interactions """
    url = serializers.HyperlinkedIdentityField(view_name='organization-detail')
    groups = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        """ Serializer/field specification """
        model = Organization
        lookup_field = 'id'
        fields = ('url', 'id', 'name', 'display_name', 'contact_name', 'contact_email', 'contact_phone',
                  'logo_url', 'users', 'groups', 'created', 'modified')
        if settings.FEATURES.get('PROJECTS_APP', False):
            fields += ('workgroups',)
        read_only = ('url', 'id', 'created')


class BasicOrganizationSerializer(serializers.ModelSerializer):
    """ Serializer for Basic Organization fields """
    url = serializers.HyperlinkedIdentityField(view_name='organization-detail')

    class Meta:
        """ Serializer/field specification """
        model = Organization
        fields = ('url', 'id', 'name', 'created', 'display_name', 'logo_url')
        lookup_field = 'id'
        read_only = ('url', 'id', 'created',)
