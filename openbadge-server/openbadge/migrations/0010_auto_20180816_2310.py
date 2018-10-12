# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0009_hub_all_ip_addresses'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unsync',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('unsync_ts', models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='unsync',
            name='member',
            field=models.ForeignKey(related_name='unsyncs', to='openbadge.Member'),
        ),
    ]
