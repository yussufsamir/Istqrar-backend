# gameya/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Gameya(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('INACTIVE', 'Inactive'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_gameyas')
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_members = models.PositiveIntegerField(default=0)
    duration_months = models.PositiveIntegerField()
    current_round = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.status})"


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    gameya = models.ForeignKey(Gameya, on_delete=models.CASCADE, related_name='memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    payout_order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'gameya') # Ensure a user can join a gameya only once

    def __str__(self):
        return f"{self.user.username} in {self.gameya.name}"


class Contribution(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.PositiveIntegerField()
    paid_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.membership.user.username} - {self.amount} ({'Paid' if self.confirmed else 'Pending'})"
