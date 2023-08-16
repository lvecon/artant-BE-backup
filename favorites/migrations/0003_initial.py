# Generated by Django 4.2.3 on 2023-08-01 13:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("favorites", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="favoritesitem",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites_items",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="favoriteshop",
            name="shop",
            field=models.ManyToManyField(
                related_name="favorites_shop", to="users.shop"
            ),
        ),
        migrations.AddField(
            model_name="favoriteshop",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites_shops",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
