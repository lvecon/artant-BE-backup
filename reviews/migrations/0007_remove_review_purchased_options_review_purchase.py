# Generated by Django 4.2.3 on 2023-12-26 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "purchases",
            "0005_purchaseline_product_name_purchaseline_product_price_and_more",
        ),
        ("reviews", "0006_remove_review_purchased_options_alter_review_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="purchase",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="purchases.purchaseline",
            ),
            preserve_default=False,
        ),
    ]