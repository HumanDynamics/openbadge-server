# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import django.contrib.auth.models
import django.utils.timezone
import django.core.validators
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenBadgeUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='email address', db_index=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
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
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('uuid', models.CharField(unique=True, max_length=64, db_index=True)),
                ('data_type', models.CharField(max_length=64)),
                ('last_update_timestamp', models.DecimalField(null=True, max_digits=20, decimal_places=3, blank=True)),
                ('filepath', models.CharField(unique=True, max_length=65, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=64)),
                ('god', models.BooleanField(default=False)),
                ('uuid', models.CharField(unique=True, max_length=64, db_index=True)),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True)),
                ('last_seen_ts', models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3)),
                ('last_hub_time_ts', models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('version', models.DecimalField(max_digits=5, decimal_places=2)),
                ('uuid', models.CharField(unique=True, max_length=64, db_index=True)),
                ('start_time', models.DecimalField(null=True, max_digits=20, decimal_places=3)),
                ('end_time', models.DecimalField(null=True, max_digits=20, decimal_places=3, blank=True)),
                ('last_update_timestamp', models.DecimalField(null=True, max_digits=20, decimal_places=3, blank=True)),
                ('last_update_index', models.IntegerField(null=True, blank=True)),
                ('ending_method', models.CharField(max_length=16, null=True, blank=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('log_file', models.FileField(storage=openbadge.models.OverwriteStorage(), upload_to=openbadge.models.upload_to, blank=True)),
                ('hub', models.ForeignKey(related_name='meetings', to='openbadge.Hub')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('id', models.PositiveSmallIntegerField(primary_key=True, validators=[django.core.validators.MaxValueValidator(15999), django.core.validators.MinValueValidator(1)], serialize=False, editable=False, blank=True, unique=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('name', models.CharField(max_length=64)),
                ('badge', models.CharField(unique=True, max_length=64)),
                ('observed_id', models.PositiveSmallIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('comments', models.CharField(default=b'', max_length=240, blank=True)),
                ('last_audio_ts', models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3)),
                ('last_audio_ts_fract', models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3)),
                ('last_proximity_ts', models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3)),
                ('last_contacted_ts', models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3)),
                ('last_unsync_ts', models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3)),
                ('last_voltage', models.DecimalField(default=Decimal('0'), max_digits=5, decimal_places=3)),
                ('last_seen_ts', models.DecimalField(default=Decimal('0'), max_digits=20, decimal_places=3)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(db_index=True, unique=True, max_length=10, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=64)),
                ('advertisement_project_id', models.IntegerField(default=1, unique=True, validators=[django.core.validators.MaxValueValidator(254), django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='member',
            name='project',
            field=models.ForeignKey(related_name='members', to='openbadge.Project'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='project',
            field=models.ForeignKey(related_name='meetings', to='openbadge.Project'),
        ),
        migrations.AddField(
            model_name='hub',
            name='project',
            field=models.ForeignKey(related_name='hubs', to='openbadge.Project', null=True),
        ),
        migrations.AddField(
            model_name='datafile',
            name='hub',
            field=models.ForeignKey(related_name='data', to='openbadge.Hub'),
        ),
        migrations.AddField(
            model_name='datafile',
            name='project',
            field=models.ForeignKey(related_name='data', to='openbadge.Project', null=True),
        ),
        migrations.AddField(
            model_name='beacon',
            name='project',
            field=models.ForeignKey(related_name='beacons', to='openbadge.Project'),
        ),
    ]
