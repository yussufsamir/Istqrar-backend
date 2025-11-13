from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    expertise = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Mentor: {self.user.username}"


class GrantApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grant_applications')
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_grants')
    project_title = models.CharField(max_length=200)
    description = models.TextField()
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Grant: {self.project_title} ({self.status})"
