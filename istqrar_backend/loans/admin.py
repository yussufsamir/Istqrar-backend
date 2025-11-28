from django.contrib import admin
from .models import Loan, Repayment

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'interest_rate', 'created_at', 'approved_at')
    list_filter = ('status',)
    search_fields = ('user__username',)
    readonly_fields = ('approved_at',)

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'payment_date', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('loan__user__username',)
