from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.generic.base import TemplateResponseMixin
from django.utils import timezone
from datetime import timedelta

from .models import SubscriptionPlan, UserSubscriptionPlan

# Create your views here.
class SubscriptionListView(ListView):
    template_name = 'subscriptions/subscriptions_list.html'
    queryset = SubscriptionPlan.objects.all()
    context_object_name = 'subscriptions'

class RequestFreeSubscriptionView(LoginRequiredMixin, View, TemplateResponseMixin):

    template_name = 'subscriptions/subscriptions-confirm.html'
    
    def post(self, request, *args, **kwargs):
        user = request.user
        plan = SubscriptionPlan.objects.get(title='QUARTER')
        user_plan, created = UserSubscriptionPlan.objects.get_or_create(user=user, defaults={'subscription_plan':plan,'expiry_date':timezone.now()+timedelta(days=28)})

        print(user_plan, created)

        if not created:
            messages.error(request, "You were already a subscriber!")
            return redirect('subscriptions')

        return self.render_to_response({})
        
            