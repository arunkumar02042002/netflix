
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic.base import TemplateResponseMixin
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMultiAlternatives
from django.views.generic import TemplateView

from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.utils import timezone


from .models import Order
from subscriptions.models import SubscriptionPlan
from common.razorpay_utils import razorpay_client

from subscriptions.models import UserSubscriptionPlan
from datetime import timedelta

from io import BytesIO
from xhtml2pdf import pisa


# Create your views here.

class OrderFailedView(TemplateView):
    template_name = 'orders/payement_failed.html'


class OrderSuccessView(TemplateView):
    template_name = 'orders/payement_success.html'


class PlaceOrderView(LoginRequiredMixin, View, TemplateResponseMixin):
    template_name = 'orders/order_summary.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        order = Order.objects.filter(user=user, payment_status=3).order_by("-datetime_of_payment").first()

        callback_url = 'http://'+ str(get_current_site(request))+"/orders/confirm/"
        return self.render_to_response({
            'order':order,
            'callback_url':callback_url,
            'razorpay_key_id':settings.RAZORPAY_KEY_ID,
            'amount':order.total_amount**100
        })

    def post(self, request, *args, **kwargs):
        subscription_uuid = request.POST.get('subscription_uuid')
        
        subscription_plan = get_object_or_404(SubscriptionPlan, uuid=subscription_uuid)

        user = request.user
        order, created = Order.objects.get_or_create(
            user=user,
            subscription_plan=subscription_plan,
            total_amount=subscription_plan.amount,
            payment_status=3,
            )
        
        callback_url = 'http://'+ str(get_current_site(request))+"/orders/confirm/"
        razorpay_order_id = razorpay_client.create_order(original_amount=order.total_amount, receipt=order.order_id,)

        if not razorpay_order_id:
            messages.error("Could not create order at razorpay. Please try after some time.")
            return redirect(reverse("subscription-buy"))
        
        order.razorpay_order_id = razorpay_order_id
        order.save()

        return render(request,
            'orders/order_summary.html',
            context={
                'order':order,
                'callback_url':callback_url,
                'razorpay_key_id':settings.RAZORPAY_KEY_ID,
                'amount':order.total_amount**100,
            })
    

@csrf_exempt
def order_confirm_view(request):
    if request.method == 'POST':
        try:

            # Data Sent by the Rayzor Pay
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id','')
            razorpay_signature = request.POST.get('razorpay_signature','')

            params_dict = { 
            'razorpay_order_id': razorpay_order_id, 
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
            }

            # In case of failed transaction razorpay returns empty razorpay_order_id
            # So we can not fetch the order instance
            order_instance = Order.objects.prefetch_related('user', 'subscription_plan').filter(razorpay_order_id=razorpay_order_id).first()

            if not order_instance:
                return redirect('order-failed')
            
            # For unsuccessful payment razorpay returns empty ids.
            try:
                # Verify the signature for
                result = razorpay_client.client.utility.verify_payment_signature(params_dict)
            except Exception as e:
                print(e)
                order_instance.payment_status = 2
                order_instance.save()
                return redirect('order-failed')

            # Store to the order instance
            order_instance.razorpay_payment_id = razorpay_payment_id
            order_instance.razorpay_signature = razorpay_signature
            order_instance.save()

            # Result True indiacates that there was no tempering
            if result is True:
                amount = order_instance.total_amount * 100 

                try:
                    # Capture the payment otherwise payment would get refunded
                    razorpay_client.client.payment.capture(razorpay_payment_id, amount)
                    
                    order_instance.payment_status = 1
                    order_instance.save()

                    subscription_plan = order_instance.subscription_plan

                    user = order_instance.user
                    user_plan, created = UserSubscriptionPlan.objects.get_or_create(user=user, subscription_plan=subscription_plan)

                    now = timezone.now()
                    if user_plan.expiry_date > now:
                        user_plan.expiry_date = user_plan.expiry_date+timedelta(days=subscription_plan.months*28)
                    else:
                        user_plan.expiry_date = now+timedelta(days=subscription_plan.months*28)
                        
                    user_plan.save()

                    mail_subject = 'Order Confirmation Mail'
                    context_dict = {
                        'user': order_instance.user,
                        'order': order_instance
                    }
                    
                    template = get_template('orders/email_invoice.html')
                    message  = template.render(context_dict)
                    to_email = order_instance.user.email

                    email = EmailMultiAlternatives(
                        mail_subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [to_email]
                    )
                    email.send(fail_silently=False)

                    return redirect('order-success')
                except Exception as e:
                    print(e)
                    order_instance.payment_status = 2
                    order_instance.save()
                    return redirect('order-failed')
            else:
                order_instance.payment_status = 2
                order_instance.save()
                return redirect('order-failed')
            
        except Exception as e:
            print(e)
            return redirect('internal-server-error')