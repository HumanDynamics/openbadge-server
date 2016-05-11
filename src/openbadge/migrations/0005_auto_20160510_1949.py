# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0004_auto_20160502_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='log_file',
            field=models.FileField(storage=openbadge.models.OverwriteStorage(), upload_to=openbadge.models.upload_to, blank=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='moderator',
            field=models.ForeignKey(blank=True, to='openbadge.StudyMember', null=True),
        ),
    ]
