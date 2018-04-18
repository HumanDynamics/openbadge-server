# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='project',
            field=models.ForeignKey(related_name='data', to='openbadge.Project', null=True),
        ),
    ]
