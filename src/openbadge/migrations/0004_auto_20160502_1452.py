# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0003_auto_20160502_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='log_file',
            field=models.FileField(upload_to=openbadge.models.upload_to, blank=True),
        ),
    ]
