# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0005_auto_20160510_1949'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisualizationRanges',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('group', models.ForeignKey(related_name='visualization_ranges', to='openbadge.StudyGroup')),
            ],
        ),
        migrations.AddField(
            model_name='meeting',
            name='location',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='show_visualization',
            field=models.BooleanField(default=False),
        ),
    ]
