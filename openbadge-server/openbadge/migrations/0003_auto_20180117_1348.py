# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0002_datafile_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='badge',
            field=models.CharField(unique=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_audio_ts',
            field=models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_proximity_ts',
            field=models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3),
        ),
    ]
