from django.db import models
from django.utils import timezone
from accounts.models import User
import uuid
# Create your models here.

class SubscriptionPlan(models.Model):

    PLAN_CHOICES = [
        ('QUARTER', '3 Months'),
        ('HALF', '6 months'),
        ('YEAR', '1 Year')
    ]

    uuid = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(choices=PLAN_CHOICES, max_length=10, unique=True)
    amount = models.PositiveIntegerField(default=0)
    months = models.PositiveIntegerField(default=4)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
    
class UserSubscriptionPlan(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='plan')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    expiry_date = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"user_{self.user_id}_plan_{self.subscription_plan_id}"