
# Create your models here.
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet - {self.balance}"

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('CONTRIBUTION', 'Gameya Contribution'),
        ('PAYOUT', 'Gameya Payout'),
        ('LOAN_DISBURSE', 'Loan Disbursement'),
        ('LOAN_REPAY', 'Loan Repayment'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_id = models.CharField(max_length=100, blank=True, null=True)  # can link to Gameya or Loan
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} ({self.amount})"
