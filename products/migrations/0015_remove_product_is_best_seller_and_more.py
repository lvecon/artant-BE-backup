# Generated by Django 4.2.3 on 2023-08-09 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0014_alter_productimage_product"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="is_best_seller",
        ),
        migrations.RemoveField(
            model_name="product",
            name="processing_time",
        ),
        migrations.AddField(
            model_name="product",
            name="has_variations",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="is_customizable",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="is_digital",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="item_height",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="item_length",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="item_weight",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="item_weight_unit",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="item_width",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="processing_max",
            field=models.CharField(default=3, max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="processing_min",
            field=models.CharField(default=1, max_length=32),
            preserve_default=False,
        ),
    ]
