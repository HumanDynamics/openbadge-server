# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0010_meeting_ending_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='DictPlotData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_name', models.CharField(max_length=32)),
                ('total_duration_of_meetings', models.CharField(max_length=32)),
                ('longest_meeting_date', models.CharField(max_length=32)),
                ('avg_speaking_time', models.CharField(max_length=32)),
                ('total_meeting_count', models.CharField(max_length=32)),
            ],
        ),
    ]
