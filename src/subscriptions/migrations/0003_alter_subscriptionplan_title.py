# Generated by Django 5.0.5 on 2024-05-13 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0002_subscriptionplan_amount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscriptionplan",
            name="title",
            field=models.CharField(
                choices=[
                    ("QUARTER", "3 Months"),
                    ("HALF", "6 months"),
                    ("YEAR", "1 Year"),
                ],
                max_length=10,
                unique=True,
            ),
        ),
    ]
