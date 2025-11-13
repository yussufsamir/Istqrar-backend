# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('USER', 'User'),
        ('MENTOR', 'Mentor'),
        ('INVESTOR', 'Investor'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    income_range = models.CharField(max_length=50, blank=True, null=True)
    business_goal = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Profile - {self.user.username}"


class TrustScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trust_score')
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}"
