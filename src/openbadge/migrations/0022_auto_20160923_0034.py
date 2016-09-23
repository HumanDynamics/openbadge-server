# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0021_auto_20160922_0255'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='init_audio_ts',
            new_name='last_audio_ts',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='init_audio_ts_fract',
            new_name='last_audio_ts_fract',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='init_proximity_ts',
            new_name='last_proximity_ts',
        ),
    ]
