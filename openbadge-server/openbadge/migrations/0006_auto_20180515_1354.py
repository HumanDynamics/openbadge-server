# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0005_auto_20180511_2151'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datafile',
            old_name='last_update_timestamp',
            new_name='last_chunk',
        ),
        migrations.AddField(
            model_name='datafile',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 9, 17, 54, 40, 184045, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
