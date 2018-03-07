# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0003_auto_20180307_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beacon',
            name='id',
            field=models.PositiveSmallIntegerField(primary_key=True, validators=[django.core.validators.MaxValueValidator(32000), django.core.validators.MinValueValidator(16000)], serialize=False, editable=False, blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='id',
            field=models.PositiveSmallIntegerField(primary_key=True, validators=[django.core.validators.MaxValueValidator(15999), django.core.validators.MinValueValidator(1)], serialize=False, editable=False, blank=True, unique=True),
        ),
    ]
