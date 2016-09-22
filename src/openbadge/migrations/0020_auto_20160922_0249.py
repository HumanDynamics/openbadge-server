# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal

class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0019_auto_20160808_0113'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='init_audio_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='init_audio_ts_fract',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='init_proximity_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
            preserve_default=False,
        ),
    ]
