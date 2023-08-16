# Generated by Django 4.2.3 on 2023-08-01 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("products", "0001_initial"),
        ("favorites", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="favoritesitem",
            name="product",
            field=models.ManyToManyField(
                related_name="favorites_item", to="products.product"
            ),
        ),
    ]
