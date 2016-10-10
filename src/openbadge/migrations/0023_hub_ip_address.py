# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0022_auto_20160923_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='hub',
            name='ip_address',
            field=models.GenericIPAddressField(null=True, blank=True),
        ),
    ]
