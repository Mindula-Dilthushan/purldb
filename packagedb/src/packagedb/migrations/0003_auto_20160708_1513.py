# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-08 22:13
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packagedb', '0002_auto_20160707_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='uri',
            field=models.CharField(db_index=True, max_length=2048, unique=True),
        ),
    ]
