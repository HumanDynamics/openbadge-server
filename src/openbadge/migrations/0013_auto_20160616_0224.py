# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0012_auto_20160615_2011'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DictPlotData',
            new_name='WeeklyGroupReport',
        ),
    ]
