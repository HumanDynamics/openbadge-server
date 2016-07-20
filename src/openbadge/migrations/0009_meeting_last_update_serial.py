# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0008_hub_god'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='last_update_serial',
            field=models.IntegerField(null=True),
        ),
    ]
