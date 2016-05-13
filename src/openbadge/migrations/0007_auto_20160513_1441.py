# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0006_auto_20160513_1428'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisualizationRange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
            ],
        ),
        migrations.RemoveField(
            model_name='visualizationranges',
            name='group',
        ),
        migrations.RemoveField(
            model_name='studygroup',
            name='show_widget',
        ),
        migrations.DeleteModel(
            name='VisualizationRanges',
        ),
        migrations.AddField(
            model_name='visualizationrange',
            name='group',
            field=models.ForeignKey(related_name='visualization_ranges', to='openbadge.StudyGroup'),
        ),
    ]
