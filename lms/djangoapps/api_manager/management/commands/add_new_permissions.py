from django.core.management.base import BaseCommand

import uuid
import json
from django.core.exceptions import ObjectDoesNotExist

from api_manager.models import GroupRelationship, GroupProfile
from django.contrib.auth.models import User, Group
from organizations.models import Organization, OrganizationGroupUser

class Command(BaseCommand):
    help = """Repair users that are assistants and observers on every course
example:
    manage.py lms add_new_permissions --settings={aws, devstack}
"""

    def handle(self, *args, **options):
        
        group_type = "permission"
        original_group_name = "mcka_role_company_admin"
        
        try:
            mcka_company_admin = Group.objects.get(name__icontains=original_group_name)
            print "Found company admin group ("+original_group_name+"), id: " + str(mcka_company_admin.id)
        
        except ObjectDoesNotExist:
            print "Creating new company admin group (mcka_role_company_admin)..."
            mcka_company_admin = Group.objects.create(name=str(uuid.uuid4()))
            mcka_company_admin.name = '{:04d}: {}'.format(mcka_company_admin.id, original_group_name)
            mcka_company_admin.record_active = True
            mcka_company_admin.save()
            print "Created successfuly company admin group (mcka_role_company_admin), id: " + str(mcka_company_admin.id)
        
        try:
            group_relationship = GroupRelationship.objects.get(group_id=mcka_company_admin.id)
        
        except ObjectDoesNotExist:
            # Create a corresponding relationship management record
            group_relationship = GroupRelationship.objects.create(group_id=mcka_company_admin.id, parent_group=None)

        # Create a corresponding profile record (for extra meta info)
        profile, _ = GroupProfile.objects.get_or_create(
            group_id=mcka_company_admin.id,
            group_type=group_type,
            name=original_group_name,
            data=json.dumps({})
        )

        all_organizations = Organization.objects.all()
        counter_of_old_orgs = 0
        print "Fetched " + str(len(all_organizations)) + " organizations!"
        for organization in all_organizations:
            try:
                group = Group.objects.get(id=mcka_company_admin.id, organizations=organization.id)
            except ObjectDoesNotExist:
                organization.groups.add(mcka_company_admin)
                organization.save() 
                counter_of_old_orgs += 1

        print "Number of organizations to update: " + str(counter_of_old_orgs)
        print "All organizations are updated!"
