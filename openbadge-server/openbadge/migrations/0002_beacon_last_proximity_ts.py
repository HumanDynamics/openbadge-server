# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='beacon',
            name='last_proximity_ts',
            field=models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3),
        ),
    ]
