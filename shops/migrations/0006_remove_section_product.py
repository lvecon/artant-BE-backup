# Generated by Django 4.2.3 on 2023-11-26 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shops", "0005_delete_shoptag"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="section",
            name="product",
        ),
    ]
