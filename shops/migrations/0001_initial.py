# Generated by Django 4.2.3 on 2023-11-25 10:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Section",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=64)),
                ("rank", models.PositiveIntegerField(null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Shop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("avatar", models.URLField(blank=True, null=True)),
                ("background_pic", models.URLField(blank=True, null=True)),
                ("shop_name", models.CharField(max_length=256)),
                (
                    "description_title",
                    models.CharField(blank=True, max_length=256, null=True),
                ),
                (
                    "description",
                    models.TextField(blank=True, max_length=2000, null=True),
                ),
                (
                    "announcement",
                    models.CharField(blank=True, max_length=256, null=True),
                ),
                ("expiration", models.TimeField(blank=True, null=True)),
                ("cancellation", models.BooleanField(default=True)),
                (
                    "shop_policy_updated_at",
                    models.DateField(
                        blank=True, default=datetime.date.today, null=True
                    ),
                ),
                ("instagram_url", models.URLField(blank=True, null=True)),
                ("facebook_url", models.URLField(blank=True, null=True)),
                ("website_url", models.URLField(blank=True, null=True)),
                ("is_star_seller", models.BooleanField(default=False)),
                ("image_1", models.URLField(blank=True, null=True)),
                ("image_2", models.URLField(blank=True, null=True)),
                ("image_3", models.URLField(blank=True, null=True)),
                ("image_4", models.URLField(blank=True, null=True)),
                ("image_5", models.URLField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ShopTag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=64)),
                ("description", models.CharField(max_length=256)),
                (
                    "shop",
                    models.ManyToManyField(
                        blank=True, related_name="tags", to="shops.shop"
                    ),
                ),
            ],
        ),
    ]
