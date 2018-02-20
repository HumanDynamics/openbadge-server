# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beacon',
            name='beacon_id',
            field=models.PositiveSmallIntegerField(default=0, unique=True, validators=[django.core.validators.MaxValueValidator(32000), django.core.validators.MinValueValidator(16000)]),
        ),
        migrations.AlterField(
            model_name='member',
            name='member_id',
            field=models.PositiveSmallIntegerField(default=0, unique=True, validators=[django.core.validators.MaxValueValidator(15999), django.core.validators.MinValueValidator(1)]),
        ),
    ]
