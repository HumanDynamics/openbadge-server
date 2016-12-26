# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0024_auto_20161222_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hub',
            name='last_seen_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_seen_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
        ),
    ]
