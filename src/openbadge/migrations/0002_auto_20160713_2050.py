# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='hub_uuid',
            new_name='hub',
        ),
    ]
