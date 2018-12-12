from __future__ import unicode_literals

from django.db import models, migrations
import openbadge.models


class Migration(migrations.Migration):

    dependencies = [
        ('openbadge', '0010_auto_20180816_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unsync',
            name='unsync_ts',
            field=models.DecimalField(default=openbadge.models._now_as_epoch, max_digits=20, decimal_places=3, db_index=True),
        ),
    ]
