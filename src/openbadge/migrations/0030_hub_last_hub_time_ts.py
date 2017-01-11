# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0029_datafile'),
    ]

    operations = [
        migrations.AddField(
            model_name='hub',
            name='last_hub_time_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
        ),
    ]
