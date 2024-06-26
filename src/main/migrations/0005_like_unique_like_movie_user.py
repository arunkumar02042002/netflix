# Generated by Django 5.0.6 on 2024-05-23 14:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_alter_moviewishlist_movie"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="like",
            constraint=models.UniqueConstraint(
                fields=("user_id", "movie_id"), name="unique_like_movie_user"
            ),
        ),
    ]
