from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL

class Loan(models.Model):

    # 📌 STATUS OPTIONS (must be INSIDE the model)
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
    ]

    # 📌 REPAYMENT PERIOD OPTIONS
    REPAYMENT_CHOICES = [
        (3, "3 Months"),
        (6, "6 Months"),
        (12, "12 Months"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()

    repayment_period = models.IntegerField(
        choices=REPAYMENT_CHOICES,
        default=6
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,     # <-- USE THE ONE INSIDE THE MODEL
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    national_id_document = models.FileField(
        upload_to='loan_docs/national_ids/',
        null=True,
        blank=True
    )
    proof_of_savings_document = models.FileField(
        upload_to='loan_docs/proof_of_savings/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Loan #{self.id} - {self.user} ({self.status})"


class Repayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Repayment for Loan {self.loan.id} - {self.amount} ({'Paid' if self.is_paid else 'Pending'})"
