# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0014_weeklygroupreport_week_num'),
    ]

    operations = [
        migrations.RenameField(
            model_name='weeklygroupreport',
            old_name='group_name',
            new_name='group_key',
        ),
    ]
