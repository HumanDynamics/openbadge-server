# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import openbadge.models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0002_auto_20160427_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='meeting',
            name='log_file',
            field=models.FileField(default='', upload_to=openbadge.models.upload_to),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='members',
            field=models.TextField(default=b'[]', blank=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='uuid',
            field=models.CharField(default=datetime.datetime(2016, 5, 2, 14, 52, 30, 478780, tzinfo=utc), unique=True, max_length=64, db_index=True),
            preserve_default=False,
        ),
    ]
