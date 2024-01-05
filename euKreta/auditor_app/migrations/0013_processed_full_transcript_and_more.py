# Generated by Django 4.2.2 on 2023-12-09 09:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auditor_app", "0012_alter_processed_detailsshared"),
    ]

    operations = [
        migrations.AddField(
            model_name="processed",
            name="full_transcript",
            field=models.TextField(default=""),
        ),
        migrations.AlterField(
            model_name="processed",
            name="DetailsShared",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="processed",
            name="Transcript",
            field=models.JSONField(default=list),
        ),
    ]