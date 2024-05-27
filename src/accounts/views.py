from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings


from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site

from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import TemplateView

from .tokens import account_activation_token
from .forms import UserCreationForm, UserProfileUpdateForm

from accounts.models import Profile

User = get_user_model()

# Create your views here.
class RegisterView(View, TemplateResponseMixin):
    form_class = UserCreationForm
    template_name = "registration/signup.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
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
        messages.success(request, f"Glad you're here, {user.username}. Login to continue.")
        return redirect(reverse("login"))
    else:
        messages.error(request, f"Activation link is invalid or your account is already verified! Login to continue.")
        return redirect(reverse("login"))

   
class UserLoginView(auth_views.LoginView):
    form_class = AuthenticationForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        
        if form.is_valid():

            auth_login(request, form.get_user())
            remember_me = request.POST.get('remember_me')

            if remember_me:
                request.session.set_expiry(7 * 24 * 60 * 60)
            messages.success(request, "You just hoped into the server!")
            return redirect('home')
        
        else:
            messages.error(request, "Login Failed. Please correct the errors")
            return self.form_invalid(form)
        

class InternalServerErrorView(TemplateView):
    template_name = '500.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = self.render_to_response(context)
        response.status_code = 500
        return response


class PageNotFoundView(TemplateView):
    template_name = '404.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = self.render_to_response(context)
        response.status_code = 404
        return response


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/user_profile.html'


class UserProfileUpdateView(LoginRequiredMixin, TemplateResponseMixin, View):

    template_name = 'registration/user_profile_update.html'
    form_class = UserProfileUpdateForm

    def get(self, request, *args, **kwargs):
        user = request.user
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_img': user.profile.profile_img,
            'bio': user.profile.bio,
        }
        return self.render_to_response({'form':self.form_class(initial=initial_data)})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, files=request.FILES, instance=request.user.profile)

        if form.is_valid() is False:
            messages.error(request, "Please correct the errors")
            return self.render_to_response({'form':self.form_class})

        cleaned_data = form.cleaned_data

        # Update User
        user = request.user
        user.first_name = cleaned_data.pop('first_name')
        user.last_name = cleaned_data.pop('last_name')
        user.save()

        # Update profile
        profile = form.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')