# Generated by Django 4.2.3 on 2023-12-18 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product_attributes", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="producttag",
            old_name="tag",
            new_name="name",
        ),
    ]