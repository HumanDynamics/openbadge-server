# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0002_auto_20180220_1655'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beacon',
            old_name='beacon',
            new_name='badge',
        ),
    ]
