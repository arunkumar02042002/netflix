from django.http import HttpResponse
from django.shortcuts import HttpResponse, redirect
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from django.contrib.auth import views as auth_views

from .tokens import account_activation_token
from .forms import UserCreationForm

from accounts.models import Profile

User = get_user_model()

# Create your views here.
class RegisterView(View, TemplateResponseMixin):
    form_class = UserCreationForm
    template_name = "registration/signup.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response({"form": self.form_class()})

    def post(self, request, *args, **kwargs):
        user_email = request.POST.get("email")
        try:
            existing_user = User.objects.get(email=user_email)
            if existing_user.is_active == False:
                existing_user.delete()
        except Exception:
            pass

        form = self.form_class(request.POST)
        if form.is_valid() is False:
            return self.render_to_response(context={"form": form})
        
        user = form.save()
        user.is_active = False
        user.save()

        current_site = get_current_site(request)

        mail_subject = 'Activate your account.'
        message = render_to_string("registration/acc_active_mail.html", {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })
        to_email = user.email

        try:
            send_mail(
                subject=mail_subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[to_email],
                fail_silently=False
            )
            messages.success(request, "An account verification link has been sent to your email id.")

        except Exception:
            form.add_error('', 'Error Occurred while Sending Email, Try Again')
            messages.error(request, "Error occurred while sending mail")
            return self.render_to_response({'form': form})

        return self.render_to_response({"form": self.form_class()})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None
    
    if user is not None and account_activation_token.check_token(user, token) is True:
        user.is_active = True
        user.save()
        profile = Profile.objects.create(user=user)
        messages.success(request, f"Glad you're here, {{request.user.username}}. Login to continue.")
        return redirect(reverse("login"))
    else:
        return HttpResponse("Activation link is invalid or your account is already verified! Try to login")