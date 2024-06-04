# Movie APP

## Introduction
The Movie APP is a comprehensive web application that allows users to browse, comment, like, and add movies to their wishlist. It also includes user authentication, subscription management, and order processing functionalities.


## Walk Through Video

<a href="https://drive.google.com/file/d/1WvXMVyagfrnzJVs2m2ba6QXYbrJNbfDF/view?usp=sharing" target="_blank">Video</a>


## Features

1. User authentication and profile management
2. Movie browsing with detailed views
3. Like and dislike movies
4. Add or remove movies from the wishlist
5. Comment on movies
6. Subscription management
7. Order processing for subscriptions
8. Error handling and debugging tools

# Project Structure

1. Config URLs (config.urls)

The config URLs handle the main routing for the application, including error pages, user account management, subscriptions, orders, and debug tools.

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('500/', view=InternalServerErrorView.as_view(), name='internal-server-error'),
    path('404/', view=PageNotFoundView.as_view(), name='page-not-found'),
    path('accounts/', include('accounts.urls')),
    path('', include('main.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('orders/', include('orders.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
]
```

2. Account URLs (accounts.urls)
Handles user registration, activation, login, logout, password management, and profile updates.

```python
urlpatterns = [
    path('signup/', views.RegisterView.as_view(), name="signup"),
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    path('login/', view=views.UserLoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html', success_url=reverse_lazy("password_change_done")), name="password_change"),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"), name="password_change_done"),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html", success_url=reverse_lazy("password_reset_done"), email_template_name="registration/forgot_password_email.html"), name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_form.html", success_url=reverse_lazy("password_reset_complete")), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_complete"),
    path("profile/", view=views.UserProfileView.as_view(), name="profile"),
    path("profile/update/", view=views.UserProfileUpdateView.as_view(), name="profile-update"),
]
```

3. Main URLs (main.urls)

Manages the main functionality related to movies, including browsing, detailed views, wishlist, and API endpoints for movies, likes, dislikes, and comments.

```python
urlpatterns = [
    path('', view=main_views.IndexView.as_view(), name='home'),
    path('movies/', view=main_views.MovieListView.as_view(), name="movies"),
    path('movies/<slug:slug>/', view=main_views.MovieDetailView.as_view(), name='movie-details'),
    path('movies/<slug:slug>/addToWishlist/', view=main_views.AddRemoveWhislistView.as_view(), name="add-to-wishlist"),
    path('api/v1/movies/', view=main_views.MovieListApiView.as_view(), name='movie-list'),
    path('api/v1/<slug:slug>/like-dislike/', view=main_views.MovieLikeAndDislikeView.as_view(), name="movie-like-dislike"),
    path('api/v1/<slug:slug>/addComment/', view=main_views.AddCommentToMovieView.as_view(), name="add-comment-to-movie"),
    path('api/v1/wishlist/', view=main_views.WishlistListView.as_view(), name="wishlist"),
]
```

4. Orders URLs (orders.urls)
Handles the order processing for subscriptions, including placing orders, confirming them, and handling success and failure scenarios.

```python
urlpatterns = [
    path('buy/', view=PlaceOrderView.as_view(), name='buy-subscription'),
    path('confirm/', view=order_confirm_view, name='order-confirm'),
    path('success/', view=OrderSuccessView.as_view(), name='order-success'),
    path('failed/', view=OrderFailedView.as_view(), name='order-failed'),
]
```

5. Subscriptions URLs (subscriptions.urls)
Manages subscription plans and requests for free subscriptions.

```python
urlpatterns = [
    path('', SubscriptionListView.as_view(), name="subscriptions"),
    path('request/', RequestFreeSubscriptionView.as_view(), name="free-subscription"),
]
```


### Installation
To install and run this project locally, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/arunkumar02042002/movie-app.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Create a superuser:

```bash
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

6. Access the application:
```
Open your web browser and go to http://localhost:8000
```

### Usage

1. Register a new account or log in if you already have one.
2. Browse movies, view details, and add them to your wishlist.
3. Like or dislike movies and leave comments.
4. Manage your profile and subscription plans.
5. Place orders for subscriptions and handle payments.


### Acknowledgments
Thanks to all the libraries that made this project possible.