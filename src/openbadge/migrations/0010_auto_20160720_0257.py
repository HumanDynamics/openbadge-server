# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0009_meeting_last_update_serial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='last_update_timestamp',
            new_name='last_update_time',
        ),
    ]
