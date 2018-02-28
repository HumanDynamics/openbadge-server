# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0002_remove_project_project_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_id',
            field=models.IntegerField(default=0),
        ),
    ]
