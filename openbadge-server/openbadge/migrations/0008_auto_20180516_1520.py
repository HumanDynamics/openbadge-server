# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0007_auto_20180515_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='datafile',
            name='filepath',
            field=models.CharField(unique=True, max_length=128, blank=True),
        ),
    ]
