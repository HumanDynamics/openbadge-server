# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0025_member_last_voltage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hub',
            name='heartbeat',
        ),
        migrations.AddField(
            model_name='hub',
            name='last_seen_ts',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='member',
            name='last_seen_ts',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
