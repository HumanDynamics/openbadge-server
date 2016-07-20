# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0004_auto_20160714_0509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting',
            name='last_update_time',
        ),
        migrations.AddField(
            model_name='meeting',
            name='last_update_timestamp',
            field=models.IntegerField(null=True),
        ),
    ]
