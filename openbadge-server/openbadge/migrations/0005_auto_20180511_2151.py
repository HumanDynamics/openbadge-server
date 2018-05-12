# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0004_ids_and_beacons'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beacon',
            name='observed_id',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='member',
            name='observed_id',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
