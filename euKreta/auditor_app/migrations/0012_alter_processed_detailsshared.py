# Generated by Django 4.2.2 on 2023-11-27 11:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auditor_app", "0011_processed_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="processed",
            name="DetailsShared",
            field=models.JSONField(blank=True, null=True),
        ),
    ]