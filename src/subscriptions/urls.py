from django.urls import path
from .views import SubscriptionListView, RequestFreeSubscriptionView

urlpatterns = [
    path('',SubscriptionListView.as_view(), name="subscriptions"),
    path('request/', RequestFreeSubscriptionView.as_view(), name="free-subscription"),
]
