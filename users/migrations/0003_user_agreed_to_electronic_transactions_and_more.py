# Generated by Django 4.2.3 on 2024-01-04 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="agreed_to_electronic_transactions",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="agreed_to_marketing_mails",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="agreed_to_optional_privacy_policy",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="agreed_to_privacy_policy",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="agreed_to_terms_of_service",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="agreed_to_third_party_sharing",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="cell_phone_number",
            field=models.CharField(default=1, max_length=11),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="user",
            name="confirmed_age_over_14",
            field=models.BooleanField(default=False),
        ),
    ]