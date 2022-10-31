# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-23 19:15
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packagedb', '0019_auto_20181023_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='download_sha256',
            field=models.CharField(blank=True, db_index=True, help_text='SHA256 checksum hex-encoded, as in sha256sum.', max_length=64, null=True, verbose_name='download SHA256'),
        ),
    ]
