from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime

import uuid

User = get_user_model()

class Cast(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f'#{self.name}'
    
    def clean(self) -> None:
        self.title = self.title.lower()
        return super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super.save(*args, **kwargs)

class Movie(models.Model):

    GENRE_CHOICES = [
            ('ACTION', 'Action'),
            ('COMEDY', 'Comedy'),
            ('DRAMA', 'Drama'),
            ('HORROR', 'Horror'),
            ('ROMANCE', 'Romance'),
            ('SCIENCE_FICTION', 'Science Fiction'),
            ('FANTASY', 'Fantasy'),
        ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')

    uuid = models.UUIDField(default=uuid.uuid4)

    title = models.CharField(max_length=150, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    release_date = models.DateField(null=True)

    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, db_index=True)
    length = models.PositiveIntegerField(default=1)
    
    image_card = models.ImageField(upload_to='movie/images/')
    image_cover = models.ImageField(upload_to='movie/covers/')
    video = models.FileField(upload_to='movie_videos/')

    director = models.CharField(max_length=100, null=True, db_index=True)

    is_paid = models.BooleanField(default=False)

    views = models.IntegerField(default=0)
    ratings = models.FloatField(default=1.0, validators=[MaxValueValidator(10.0), MinValueValidator(1.0)], db_index=True)

    tags = models.ManyToManyField(Tag, through="MovieTag")
    casts = models.ManyToManyField(Cast, through="MovieCast")

    like_counts = models.PositiveIntegerField(default=0)

    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.title
    
    def is_high_rated(self):
        now = timezone.now()
        return self.ratings >= 8.5 and self.release_date <= now
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=30) <= self.release_date <= now
    
    def is_most_viewed(self):
        now = timezone.now()
        return self.views >= 10000 and self.release_date <= now

    def get_absolute_url(self):
        return reverse("movie-details", kwargs={"slug": self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class MovieCast(models.Model):
    cast = models.ForeignKey(Cast, on_delete=models.CASCADE, related_name="movies")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="movie_casts")

    def __str__(self) -> str:
        return f'{self.cast.name}-{self.movie.title}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cast_id", "movie_id"],
                name = "unique_movie_cast"
            )
        ]
    
class MovieTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="movies")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="movie_tags")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tag_id", "movie_id"], name="unique_movie_tag"
            )
        ]

    def __str__(self) -> str:
        return f'{self.tag__name}-{self.movie__title}'
    
class MovieWishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='wishlist_users')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "movie_id"], name="unique_movie_user"
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username}-{self.movie.title}'
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    value = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.user.username}_{self.movie.title}'
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='likes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "movie_id"],
                name = "unique_like_movie_user"
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username}_{self.movie.title}'
    

