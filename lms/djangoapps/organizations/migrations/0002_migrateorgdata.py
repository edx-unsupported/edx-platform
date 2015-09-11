# -*- coding: utf-8 -*-
import datetime
import logging

from south.db import db
from south.v2 import SchemaMigration
from django.db import connection, models, transaction

from organizations.models import Organization

log = logging.getLogger(__name__)


class Migration(SchemaMigration):

    def print_message(self, msg):
        print msg
        log.info(msg)

    def forwards(self, orm):
        if not db.dry_run:
            existing_entries = Organization.objects.all().count()
            self.print_message('EXISTING ENTRIES: {}'.format(existing_entries))
            if existing_entries == 0:
                try:
                    cursor = connection.cursor()
                    cursor.execute('INSERT INTO organizations_organization SELECT * from api_manager_organization')
                    log_msg = 'organizations entries moved from api_manager to organizations app'
                    self.print_message(log_msg)

                    cursor.execute('INSERT INTO organizations_organization_workgroups '
                                   'SELECT * from api_manager_organization_workgroups')
                    log_msg = 'organization_workgroups entries moved from api_manager to organizations app'
                    self.print_message(log_msg)

                    cursor.execute('INSERT INTO organizations_organization_users '
                                   'SELECT * from api_manager_organization_users')
                    log_msg = 'organization_users entries moved from api_manager to organizations app'
                    self.print_message(log_msg)

                    cursor.execute('INSERT INTO organizations_organization_groups '
                                   'SELECT * from api_manager_organization_groups')
                    log_msg = 'organization_groups entries moved from api_manager to organizations app'
                    self.print_message(log_msg)
                    transaction.commit()

                    # Deleting model 'Organization'
                    db.delete_table('api_manager_organization')

                    # Removing M2M table for field users on 'Organization'
                    db.delete_table('api_manager_organization_users')

                    # Removing M2M table for field groups on 'Organization'
                    db.delete_table('api_manager_organization_groups')

                    # Removing M2M table for field workgroups on 'Organization'
                    db.delete_table('api_manager_organization_workgroups')

                except Exception as e:
                    log_msg = e.message
                    self.print_message(log_msg)
            else:
                log_msg = 'oroganizations_organization is not empty. You might have already filled it.'
                self.print_message(log_msg)

    def backwards(self, orm):
        # Adding model 'Organization'
        db.create_table('api_manager_organization', (
            ('contact_email', self.gf('django.db.models.fields.EmailField')(max_length=255, null=True, blank=True)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('logo_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('contact_phone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('api_manager', ['Organization'])

        # Adding M2M table for field users on 'Organization'
        db.create_table('api_manager_organization_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm['api_manager.organization'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('api_manager_organization_users', ['organization_id', 'user_id'])

        # Adding M2M table for field groups on 'Organization'
        db.create_table('api_manager_organization_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm['api_manager.organization'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('api_manager_organization_groups', ['organization_id', 'group_id'])

        # Adding M2M table for field workgroups on 'Organization'
        db.create_table('api_manager_organization_workgroups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm['api_manager.organization'], null=False)),
            ('workgroup', models.ForeignKey(orm['projects.workgroup'], null=False))
        ))
        db.create_unique('api_manager_organization_workgroups', ['organization_id', 'workgroup_id'])

    models = {
        'api_manager.coursecontentgrouprelationship': {
            'Meta': {'unique_together': "(('course_id', 'content_id', 'group_profile'),)", 'object_name': 'CourseContentGroupRelationship'},
            'content_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'group_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api_manager.GroupProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'record_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'api_manager.coursegrouprelationship': {
            'Meta': {'object_name': 'CourseGroupRelationship'},
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'record_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'api_manager.coursemodulecompletion': {
            'Meta': {'object_name': 'CourseModuleCompletion'},
            'content_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'stage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'course_completions'", 'to': "orm['auth.User']"})
        },
        'api_manager.groupprofile': {
            'Meta': {'object_name': 'GroupProfile', 'db_table': "'auth_groupprofile'"},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True'}),
            'group_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'record_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'api_manager.grouprelationship': {
            'Meta': {'object_name': 'GroupRelationship'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent_group': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'related_name': "'child_groups'", 'null': 'True', 'blank': 'True', 'to': "orm['api_manager.GroupRelationship']"}),
            'record_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'api_manager.linkedgrouprelationship': {
            'Meta': {'object_name': 'LinkedGroupRelationship'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'from_group_relationship': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_group_relationships'", 'to': "orm['api_manager.GroupRelationship']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'record_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'to_group_relationship': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_group_relationships'", 'to': "orm['api_manager.GroupRelationship']"})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['api_manager']
