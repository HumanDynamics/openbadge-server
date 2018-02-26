# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0002_beacon_last_proximity_ts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beacon',
            name='last_proximity_ts',
        ),
    ]
