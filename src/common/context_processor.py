
from main.models import Movie
from django.utils import timezone


def top_movies(request):
    now = timezone.now()
    top_rated_movies = Movie.objects.filter(release_date__lte=now).order_by('-ratings')[:3]
    return dict(top_rated_movies=top_rated_movies)

def recently_published_movies(request):
    now = timezone.now()
    recent_movies = Movie.objects.filter(release_date__lte=now).order_by("-release_date")[:3]
    return dict(recent_movies=recent_movies)

def most_views_movies(request):
    now = timezone.now()
    most_viewed_movies = Movie.objects.filter(release_date__lte=now).order_by("-views")[:3]
    return dict(most_viewed_movies=most_viewed_movies)