# Generated by Django 4.2.3 on 2023-12-17 07:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_remove_address_address_name_remove_address_note_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="recipient_name",
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
