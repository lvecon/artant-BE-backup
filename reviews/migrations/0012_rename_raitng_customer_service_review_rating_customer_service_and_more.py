# Generated by Django 4.2.3 on 2023-08-22 06:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0011_alter_reviewreply_shop"),
    ]

    operations = [
        migrations.RenameField(
            model_name="review",
            old_name="raitng_customer_service",
            new_name="rating_customer_service",
        ),
        migrations.RenameField(
            model_name="review",
            old_name="raitng_item_quality",
            new_name="rating_item_quality",
        ),
        migrations.RenameField(
            model_name="review",
            old_name="raitng_shipping",
            new_name="rating_shipping",
        ),
    ]