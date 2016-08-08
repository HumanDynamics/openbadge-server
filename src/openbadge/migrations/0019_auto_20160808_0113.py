# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0018_auto_20160808_0103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hub',
            name='last_update',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='last_update',
        ),
        migrations.RemoveField(
            model_name='member',
            name='last_update',
        ),
        migrations.RemoveField(
            model_name='openbadgeuser',
            name='last_update',
        ),
        migrations.RemoveField(
            model_name='project',
            name='last_update',
        ),
    ]
