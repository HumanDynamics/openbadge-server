# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0006_member_last_unsync_ts'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='beacon',
            options={'ordering': ['-last_voltage']},
        ),
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['-active', '-last_voltage']},
        ),
    ]
