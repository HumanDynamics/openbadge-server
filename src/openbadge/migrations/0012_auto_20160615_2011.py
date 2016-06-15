# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0011_dictplotdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictplotdata',
            name='end_date',
            field=models.CharField(default=b'none', max_length=32),
        ),
        migrations.AddField(
            model_name='dictplotdata',
            name='start_date',
            field=models.CharField(default=b'none', max_length=32),
        ),
    ]
