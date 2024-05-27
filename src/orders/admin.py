from django.contrib import admin
from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_status', 'datetime_of_payment', 'total_amount')
    list_filter = ('payment_status',)

    def user(self, obj):
        return obj.user.email

# Register your models here.
admin.site.register(Order, OrderAdmin)