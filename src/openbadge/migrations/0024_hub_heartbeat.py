# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0023_hub_ip_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='hub',
            name='heartbeat',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
