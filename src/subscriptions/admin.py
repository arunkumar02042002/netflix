from django.contrib import admin
from .models import SubscriptionPlan, UserSubscriptionPlan

# Register your models here.
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'months')

    ordering =('title',)


class UserSubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'expiry_date')

    def user(self, obj):
        return obj.user.username
    
    def plan(self, obj):
        return obj.subscription_plan.title

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(UserSubscriptionPlan, UserSubscriptionPlanAdmin)