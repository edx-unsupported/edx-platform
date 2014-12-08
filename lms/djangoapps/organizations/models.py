"""
Django database models supporting the organizations app
"""
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import models

from model_utils.models import TimeStampedModel

if settings.FEATURES.get('PROJECTS_APP', False):
    from projects.models import Workgroup


class Organization(TimeStampedModel):
    """
    Main table representing the Organization concept.  Organizations are
    primarily a collection of Users.
    """
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    contact_email = models.EmailField(max_length=255, null=True, blank=True)
    contact_phone = models.CharField(max_length=50, null=True, blank=True)
    logo_url = models.CharField(max_length=255, blank=True, null=True)

    if settings.FEATURES.get('ORGANIZATIONS_APP', False):
        users = models.ManyToManyField(User, related_name="organizations")
        groups = models.ManyToManyField(Group, related_name="organizations")

    if settings.FEATURES.get('PROJECTS_APP', False):
        workgroups = models.ManyToManyField(Workgroup, related_name="organizations")
