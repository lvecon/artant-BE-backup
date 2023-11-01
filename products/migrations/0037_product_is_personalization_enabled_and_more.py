# Generated by Django 4.2.3 on 2023-11-01 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0036_alter_producttag_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_personalization_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="is_personalization_optional",
            field=models.BooleanField(default=False),
        ),
    ]
