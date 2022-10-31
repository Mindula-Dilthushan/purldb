# Generated by Django 3.1.3 on 2020-11-09 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packagedb', '0041_update_ordering_to_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='contains_source_code',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='extra_data',
            field=models.JSONField(blank=True, default=dict, help_text='An optional JSON-formatted field to identify additional resource attributes.'),
        ),
    ]
