# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0023_hub_ip_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('uuid', models.CharField(unique=True, max_length=64, db_index=True)),
                ('data_type', models.CharField(max_length=64)),
                ('last_update_timestamp', models.DecimalField(null=True, max_digits=20, decimal_places=3, blank=True)),
                ('log_file', models.FileField(storage=openbadge.models.OverwriteStorage(), upload_to=openbadge.models.upload_to, blank=True)),
                ('hub', models.ForeignKey(related_name='data', to='openbadge.Hub')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
