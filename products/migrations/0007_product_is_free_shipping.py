# Generated by Django 4.2.3 on 2023-12-18 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_remove_product_is_artant_star_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_free_shipping",
            field=models.BooleanField(default=False),
        ),
    ]