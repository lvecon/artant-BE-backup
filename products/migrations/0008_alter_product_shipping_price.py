# Generated by Django 4.2.3 on 2023-12-18 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0007_product_is_free_shipping"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="shipping_price",
            field=models.PositiveIntegerField(default=0),
        ),
    ]