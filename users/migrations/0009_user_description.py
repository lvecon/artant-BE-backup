# Generated by Django 4.2.3 on 2023-12-17 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_user_is_confirmed"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="description",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
