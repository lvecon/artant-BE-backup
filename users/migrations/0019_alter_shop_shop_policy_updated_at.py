# Generated by Django 4.2.3 on 2023-08-26 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0018_rename_user_shop_users"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shop",
            name="shop_policy_updated_at",
            field=models.DateField(auto_created=True),
        ),
    ]