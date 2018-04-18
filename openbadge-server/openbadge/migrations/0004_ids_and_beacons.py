# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import django.core.validators
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0003_auto_20180117_1348'),
    ]

    def set_advertisement_project_id(apps, schema_editor):
        my_model = apps.get_model('openbadge', 'Project')
        for i, model in enumerate(my_model.objects.all()):
            model.advertisement_project_id = model.id
            model.save()

    operations = [
        migrations.CreateModel(
            name='Beacon',
            fields=[
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('id', models.PositiveSmallIntegerField(primary_key=True, validators=[django.core.validators.MaxValueValidator(32000), django.core.validators.MinValueValidator(16000)], serialize=False, editable=False, blank=True, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('badge', models.CharField(unique=True, max_length=64)),
                ('observed_id', models.PositiveSmallIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('comments', models.CharField(default=b'', max_length=240, blank=True)),
                ('last_voltage', models.DecimalField(default=Decimal('0'), max_digits=5, decimal_places=3)),
                ('last_seen_ts', models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='member',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='member',
            name='comments',
            field=models.CharField(default=b'', max_length=240, blank=True),
        ),
        migrations.AddField(
            model_name='member',
            name='last_contacted_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
        ),
        migrations.AddField(
            model_name='member',
            name='last_unsync_ts',
            field=models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3),
        ),
        migrations.AddField(
            model_name='member',
            name='observed_id',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='member',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='id',
            field=models.PositiveSmallIntegerField(primary_key=True, validators=[django.core.validators.MaxValueValidator(15999), django.core.validators.MinValueValidator(1)], serialize=False, editable=False, blank=True, unique=True),
        ),
        migrations.AddField(
            model_name='beacon',
            name='project',
            field=models.ForeignKey(related_name='beacons', to='openbadge.Project'),
        ),
        # Manually populating values for existing projects
        migrations.AddField(
            model_name='project',
            name='advertisement_project_id',
            field=models.IntegerField(null=True, unique=True,
                                      validators=[django.core.validators.MaxValueValidator(254),
                                                  django.core.validators.MinValueValidator(1)]),
        ),
        migrations.RunPython(set_advertisement_project_id),
        migrations.AlterField(
            model_name='project',
            name='advertisement_project_id',
            field=models.IntegerField(default=openbadge.models._generate_advertisement_project_id, unique=True,
                                      validators=[django.core.validators.MaxValueValidator(254),
                                                  django.core.validators.MinValueValidator(1)]),
        ),

    ]
