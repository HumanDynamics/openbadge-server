# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0011_auto_20160721_1859'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='last_update_serial',
            new_name='last_update_index',
        ),
        migrations.RenameField(
            model_name='meeting',
            old_name='last_update_time',
            new_name='last_update_timestamp',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='description',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='location',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='type',
        ),
        migrations.AddField(
            model_name='meeting',
            name='version',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
