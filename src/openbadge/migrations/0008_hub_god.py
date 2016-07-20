# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0007_auto_20160716_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='hub',
            name='god',
            field=models.BooleanField(default=False),
        ),
    ]
