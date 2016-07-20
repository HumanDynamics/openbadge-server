# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0006_auto_20160716_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='last_update_timestamp',
            field=models.FloatField(null=True),
        ),
    ]
