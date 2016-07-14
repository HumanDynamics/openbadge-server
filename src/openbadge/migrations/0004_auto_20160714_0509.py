# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0003_auto_20160714_0507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='ending_method',
            field=models.CharField(max_length=16, null=True, blank=True),
        ),
    ]
