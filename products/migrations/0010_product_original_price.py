# Generated by Django 4.2.3 on 2023-08-08 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0009_rename_isbestseller_product_is_best_seller"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="original_price",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
