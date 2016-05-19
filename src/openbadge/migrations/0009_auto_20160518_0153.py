# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0008_auto_20160517_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='group',
            field=models.ForeignKey(related_name='meetings', to='openbadge.StudyGroup'),
        ),
    ]
