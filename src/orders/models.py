from typing import Any, Iterable
from django.db import models
from accounts.models import User
from subscriptions.models import SubscriptionPlan
from django.utils import timezone

import shortuuid

# Create your models here.

class Order(models.Model):
    PAYEMENT_STATUS_CHOICES = (
        (1, 'SUCCESS'),
        (2, 'FAILURE' ),
        (3, 'PENDING'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)

    total_amount = models.FloatField()
    payment_status = models.IntegerField(choices=PAYEMENT_STATUS_CHOICES, default=3)
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True) 
    datetime_of_payment = models.DateTimeField(default=timezone.now)
    notes = models.JSONField(default=dict)

    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_id and self.datetime_of_payment and self.id:
            self.order_id = self.datetime_of_payment.strftime('PAY%Y%m%dORD')+str(self.id)+shortuuid.uuid()[:10]
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.user.email + "_" + str(self.id)
    