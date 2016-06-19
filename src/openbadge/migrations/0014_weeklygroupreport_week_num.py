# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0013_auto_20160616_0224'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklygroupreport',
            name='week_num',
            field=models.CharField(default=b'none', max_length=32),
        ),
    ]
