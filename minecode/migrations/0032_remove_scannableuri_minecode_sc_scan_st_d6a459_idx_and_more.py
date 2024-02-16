# Generated by Django 5.0.1 on 2024-02-15 23:16

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("minecode", "0031_importableuri"),
        ("packagedb", "0083_delete_apiuser"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="scannableuri",
            name="minecode_sc_scan_st_d6a459_idx",
        ),
        migrations.AlterUniqueTogether(
            name="scannableuri",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="scannableuri",
            name="scan_date",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                help_text="Timestamp set to the date when a scan was taken by a worker",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="scannableuri",
            name="scan_project_url",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="URL to scan project for this Package",
                max_length=2048,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="scannableuri",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.AddIndex(
            model_name="scannableuri",
            index=models.Index(
                fields=["scan_status", "scan_date", "last_status_poll_date"],
                name="minecode_sc_scan_st_5e04d7_idx",
            ),
        ),
        migrations.RemoveField(
            model_name="scannableuri",
            name="scan_request_date",
        ),
        migrations.RemoveField(
            model_name="scannableuri",
            name="scan_uuid",
        ),
    ]
