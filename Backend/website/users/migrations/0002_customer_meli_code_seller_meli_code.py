# Generated by Django 5.1.2 on 2024-11-06 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="meli_code",
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="seller",
            name="meli_code",
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
