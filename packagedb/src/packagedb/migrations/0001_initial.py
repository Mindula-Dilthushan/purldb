# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-11 01:20
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')),
                ('uri', models.CharField(db_index=True, max_length=2048)),
                ('file_name', models.CharField(blank=True, db_index=True, help_text='File name of a Resource sometimes part of the URI properand sometimes only available through an HTTP header.', max_length=255, null=True)),
                ('sha1', models.CharField(blank=True, db_index=True, help_text='SHA1 checksum hex-encoded, as in sha1sum.', max_length=40, verbose_name='SHA1')),
                ('md5', models.CharField(blank=True, db_index=True, help_text='MD5 checksum hex-encoded, as in md5sum.', max_length=32, verbose_name='MD5')),
                ('size', models.BigIntegerField(blank=True, db_index=True, help_text='Size in bytes.', null=True)),
                ('last_modified_date', models.DateField(blank=True, help_text='Timestamp set to the last modified date of the remote Resource, such as the modified date of a file, the lastmod value on a sitemap or the modified date returned by an HTTP resource.', null=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(help_text='Metadata collected for this package.')),
            ],
            options={
                'ordering': ['uri'],
            },
        ),
    ]
