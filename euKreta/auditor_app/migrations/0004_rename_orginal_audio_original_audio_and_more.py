# Generated by Django 4.2.2 on 2023-09-19 15:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auditor_app", "0003_alter_processed_detailsshared_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="orginal_audio",
            new_name="original_audio",
        ),
        migrations.AlterField(
            model_name="processed",
            name="DetailsShared",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="processed",
            name="processed_file",
            field=models.FileField(blank=True, null=True, upload_to=""),
        ),
    ]
