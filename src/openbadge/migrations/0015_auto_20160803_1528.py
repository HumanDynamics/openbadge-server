# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0014_auto_20160803_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='end_time',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='last_update_timestamp',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='start_time',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=3),
        ),
    ]
