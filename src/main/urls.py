from django.urls import path

from . import views as main_views

urlpatterns = [
    path('', view=main_views.IndexView.as_view(), name='home'),
    path('movies/', view=main_views.MovieListView.as_view(), name="movies"),
    path('movies/<slug:slug>/', view=main_views.MovieDetailView.as_view(), name='movie-details'),
    path('movies/<slug:slug>/addToWishlist/', view=main_views.AddRemoveWhislistView.as_view(), name="add-to-wishlist"),

    # API Views
    path('api/v1/movies/', view=main_views.MovieListApiView.as_view(), name='movie-list'),
    path('api/v1/<slug:slug>/like-dislike/', view=main_views.MovieLikeAndDislikeView.as_view(), name="movie-like-dislike"),
    path('api/v1/<slug:slug>/addComment/', view=main_views.AddCommentToMovieView.as_view(), name="add-comment-to-movie"),
    path('api/v1/wishlist/', view=main_views.WishlistListView.as_view(), name="wishlist"),
]