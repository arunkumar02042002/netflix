# Generated by Django 5.0.6 on 2024-05-13 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_id",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
