# Generated by Django 4.2.3 on 2023-11-24 04:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="producttag",
            old_name="tag",
            new_name="name",
        ),
    ]
