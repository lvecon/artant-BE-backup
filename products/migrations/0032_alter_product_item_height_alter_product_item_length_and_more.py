# Generated by Django 4.2.3 on 2023-08-28 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0031_alter_product_original_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="item_height",
            field=models.CharField(blank=True, default=90, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="item_length",
            field=models.CharField(blank=True, default=20, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="item_width",
            field=models.CharField(blank=True, default=60, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="made_by",
            field=models.CharField(
                choices=[
                    ("I did", "I did"),
                    ("A memeber of my shop", "A memeber of my shop"),
                    ("Another company or person", "Another company or person"),
                ],
                default="I did",
                max_length=140,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_creation_date",
            field=models.CharField(
                choices=[
                    ("Made To Order", "Made To Order"),
                    ("2020-2023", "2020-2023"),
                    ("2010-2019", "2010-2019"),
                    ("2000-2009", "2010-2009"),
                    ("Before 2000", "Before 2000"),
                    ("1990-1999", "1990-1999"),
                    ("1980-1989", "1980-1989"),
                    ("1970-1979", "1970-1979"),
                    ("1960-1969", "1960-1969"),
                    ("1950-1959", "1950-1959"),
                    ("1940-1949", "1940-1949"),
                    ("1930-1939", "1930-1939"),
                    ("1920-1929", "1920-1929"),
                    ("1910-1919", "1910-1919"),
                    ("1900-1909", "1900-1909"),
                    ("1800-1899", "1800-1899"),
                    ("1700-1799", "1790-1799"),
                    ("Before 1700", "Before 1700"),
                ],
                default="Made To Order",
                max_length=140,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_type",
            field=models.CharField(
                choices=[
                    ("A finished product", "A finished product"),
                    (
                        "A supply or tool to make things",
                        "A supply or tool to make things",
                    ),
                ],
                default="A finished product",
                max_length=140,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="stock",
            field=models.PositiveIntegerField(blank=True, default=12, null=True),
        ),
    ]
