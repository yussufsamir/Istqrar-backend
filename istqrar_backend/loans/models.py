from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Loan #{self.id} - {self.user.username} ({self.status})"


class Repayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Repayment for Loan {self.loan.id} - {self.amount} ({'Paid' if self.is_paid else 'Pending'})"
