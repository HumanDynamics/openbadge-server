# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0024_hub_heartbeat'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='last_voltage',
            field=models.DecimalField(default=Decimal('0'), max_digits=5, decimal_places=3),
        ),
    ]
