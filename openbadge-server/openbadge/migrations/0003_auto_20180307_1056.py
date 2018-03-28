# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0002_auto_20180307_1045'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beacon',
            old_name='internal_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='internal_id',
            new_name='id',
        ),
        migrations.AlterField(
            model_name='project',
            name='advertisment_project_id',
            field=models.IntegerField(default=1, unique=True, validators=[django.core.validators.MaxValueValidator(254), django.core.validators.MinValueValidator(1)]),
        ),
    ]
