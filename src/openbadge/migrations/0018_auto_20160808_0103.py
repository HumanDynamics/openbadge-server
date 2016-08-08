# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0017_auto_20160807_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='hub',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 8, 1, 3, 17, 961194, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 8, 1, 3, 37, 41184, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 8, 1, 3, 42, 818065, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='openbadgeuser',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 8, 1, 3, 45, 528044, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 8, 1, 3, 48, 756753, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
