# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0010_auto_20160720_0257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='last_update_serial',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='last_update_time',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
