# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0008_auto_20180516_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='hub',
            name='all_ip_addresses',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
    ]
