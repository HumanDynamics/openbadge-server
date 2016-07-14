# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0002_auto_20160713_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
    ]
