# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='moderator',
            field=models.ForeignKey(default=1, to='openbadge.StudyMember'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='type',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
