# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0012_auto_20160802_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='version',
            field=models.DecimalField(max_digits=5, decimal_places=2),
        ),
    ]
