# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0005_member_last_contacted_ts'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='last_unsync_ts',
            field=models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3),
        ),
    ]
