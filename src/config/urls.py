"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from accounts.views import InternalServerErrorView, PageNotFoundView

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


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)