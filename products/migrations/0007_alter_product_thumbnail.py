# Generated by Django 4.2.3 on 2023-08-08 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_product_thumbnail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="thumbnail",
            field=models.URLField(),
        ),
    ]
