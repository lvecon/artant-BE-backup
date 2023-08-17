# Generated by Django 4.2.3 on 2023-08-16 07:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0015_alter_section_product_alter_section_shop_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shop",
            name="user",
            field=models.ManyToManyField(
                related_name="shops", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]