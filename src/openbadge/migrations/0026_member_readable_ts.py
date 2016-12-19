# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0025_auto_20161215_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='readable_ts',
            field=models.CharField(max_length=64, blank=True),
        ),
    ]
