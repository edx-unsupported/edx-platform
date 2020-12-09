# -*- coding: utf-8 -*-

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
from opaque_keys.edx.django.models import CourseKeyField
import util.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseStructure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('course_id', CourseKeyField(unique=True, max_length=255, verbose_name='Course ID', db_index=True)),
                ('structure_json', util.models.CompressedTextField(null=True, verbose_name='Structure JSON', blank=True)),
                ('discussion_id_map_json', util.models.CompressedTextField(null=True, verbose_name='Discussion ID Map JSON', blank=True)),
            ],
        ),
    ]
