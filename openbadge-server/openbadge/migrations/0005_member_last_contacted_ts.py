# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0004_auto_20180307_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='last_contacted_ts',
            field=models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3),
        ),
    ]
