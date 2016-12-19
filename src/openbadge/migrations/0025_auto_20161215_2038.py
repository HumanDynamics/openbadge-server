# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0024_datalog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datalog',
            name='hub',
        ),
        migrations.DeleteModel(
            name='DataLog',
        ),
    ]
