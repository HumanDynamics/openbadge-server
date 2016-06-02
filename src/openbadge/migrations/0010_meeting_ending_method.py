# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0009_auto_20160518_0153'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='ending_method',
            field=models.CharField(max_length=16, blank=True),
        ),
    ]
