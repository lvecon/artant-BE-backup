# Generated by Django 4.2.3 on 2023-10-08 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0022_alter_shop_address_alter_shop_cancellation_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="description_title",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name="shop",
            name="description",
            field=models.TextField(blank=True, max_length=2000, null=True),
        ),
    ]
