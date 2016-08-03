# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0013_auto_20160803_0454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='end_time',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='start_time',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
