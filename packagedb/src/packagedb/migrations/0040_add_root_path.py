# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-10-12 13:54
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packagedb', '0039_packageurl_python_field_updates'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='manifest_path',
        ),
        migrations.AddField(
            model_name='package',
            name='root_path',
            field=models.CharField(blank=True, help_text='The path to the root of the package documented in this manifest if any, such as a Maven .pom or a npm package.json parent directory.', max_length=1024, null=True),
        ),
    ]
