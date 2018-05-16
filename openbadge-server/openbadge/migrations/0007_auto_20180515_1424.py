# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0006_auto_20180515_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='hub',
            field=models.ForeignKey(related_name='data', to='openbadge.Hub', null=True),
        ),
    ]
