from django.urls import path
from .views import PlaceOrderView, order_confirm_view, OrderSuccessView, OrderFailedView

urlpatterns = [
    path('buy/', view=PlaceOrderView.as_view(), name='buy-subscription'),
    path('confirm/', view=order_confirm_view, name='order-confirm'),
    path('success/', view=OrderSuccessView.as_view(), name='order-success'),
    path('failed/', view=OrderFailedView.as_view(), name='order-failed'),
]
