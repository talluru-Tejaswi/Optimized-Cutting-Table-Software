from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    verification_expires = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"

class SessionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_logs')
    session_key = models.CharField(max_length=40, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} Session on {self.login_time}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}"

class ActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('register', 'Register'),
        ('update', 'Update'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

class EmailLog(models.Model):
    EMAIL_TYPES = [
        ('welcome', 'Welcome Email'),
        ('verification', 'Verification Email'),
        ('profile_update', 'Profile Update Email'),
        ('session_login', 'Session Login Notification'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    email_type = models.CharField(max_length=30, choices=EMAIL_TYPES)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    recipients = models.TextField()  # comma-separated emails
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.email_type} at {self.sent_at}"
