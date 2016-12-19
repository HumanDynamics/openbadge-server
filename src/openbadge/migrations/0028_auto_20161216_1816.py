# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0027_auto_20161216_1811'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DataLog',
            new_name='DataFile',
        ),
    ]
