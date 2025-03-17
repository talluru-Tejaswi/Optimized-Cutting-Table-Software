from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, View, TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .forms import RegistrationForm, ProfileUpdateForm
from .models import SessionLog, ActivityLog, UserProfile, EmailLog
import datetime
from django.contrib.auth.forms import AuthenticationForm

# Mixin for activity logging
class ActivityLogMixin:
    def log_activity(self, user, activity_type, description=''):
        ActivityLog.objects.create(user=user, activity_type=activity_type, description=description)

# Mixin for email notifications with logging
class EmailNotificationMixin:
    def send_email_notification(self, user, email_type, subject, template, context, recipients=None):
        recipients = recipients or [user.email]
        html_message = render_to_string(template, context)
        email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, recipients)
        email.content_subtype = 'html'
        try:
            email.send()
            success = True
        except Exception:
            success = False
        EmailLog.objects.create(
            user=user, email_type=email_type, subject=subject,
            body=html_message, recipients=", ".join(recipients), success=success
        )
        return success

class LoginView(FormView, ActivityLogMixin, EmailNotificationMixin):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        ip = self.request.META.get('REMOTE_ADDR')
        session_key = self.request.session.session_key or get_random_string(32)
        SessionLog.objects.create(user=user, ip_address=ip, session_key=session_key)
        self.log_activity(user, 'login', 'User logged in.')
        
        # Send session login notification email (if desired)
        self.send_email_notification(user, 'session_login', 'New Login Detected',
                                     'accounts/session_login_email.html', {'username': user.username, 'ip': ip})
        
        # Add a success message
        messages.success(self.request, 'You have successfully logged in.')
        
        return super().form_valid(form)

class RegisterView(FormView, ActivityLogMixin, EmailNotificationMixin):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        token = get_random_string(64)
        UserProfile.objects.create(
            user=user, verification_token=token,
            verification_expires=timezone.now() + datetime.timedelta(days=1)
        )
        context = {'username': user.username, 'token': token}
        # Send welcome/verification email
        self.send_email_notification(user, 'verification', 'Welcome to Service-Verse - Verify Your Email',
                                     'register_email.html', context)
        messages.success(self.request, 'Registration successful! Check your email to verify your account.')
        self.log_activity(user, 'register', 'User registered.')
        return super().form_valid(form)

class LogoutView(RedirectView, ActivityLogMixin):
    url = reverse_lazy('login')
    
    def get(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        SessionLog.objects.filter(user=user, logout_time__isnull=True).update(logout_time=timezone.now())
        self.log_activity(user, 'logout', 'User logged out.')
        return super().get(request, *args, **kwargs)

class EmailVerificationView(View):
    def get(self, request, token, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(verification_token=token)
            profile.email_verified = True
            profile.verification_token = ''
            profile.verification_expires = None
            profile.save()
            messages.success(request, 'Email verified successfully.')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid or expired token.')
        return redirect('login')

class ProfileUpdateView(FormView, ActivityLogMixin, EmailNotificationMixin):
    template_name = 'accounts/profile_update.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('dashboard')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        user = form.save()
        subject = 'Your Email Has Been Updated'
        self.send_email_notification(user, 'profile_update', subject, 'profile_update_email.html',
                                     {'username': user.username, 'new_email': user.email})
        self.log_activity(user, 'update', 'User updated email.')
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

class DashboardView(TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'session_logs': user.session_logs.all(),
            'activity_logs': user.activity_logs.all(),
            'notifications': user.notifications.all(),
            'email_logs': user.email_logs.all(),
        })
        return context
