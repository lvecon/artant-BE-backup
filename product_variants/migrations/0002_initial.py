# Generated by Django 4.2.3 on 2024-01-12 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("product_variants", "0001_initial"),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="variation",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variations",
                to="products.product",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="option_one",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants_as_option_one",
                to="product_variants.variationoption",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="option_two",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants_as_option_two",
                to="product_variants.variationoption",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants",
                to="products.product",
            ),
        ),
    ]
