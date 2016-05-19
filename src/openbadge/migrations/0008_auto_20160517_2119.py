# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0007_auto_20160513_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='name',
            field=models.CharField(unique=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='studymember',
            name='email',
            field=models.EmailField(unique=True, max_length=254),
        ),
    ]
