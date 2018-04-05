# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0009_auto_20180403_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='last_contacted_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_unsync_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
        ),
    ]
