from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'reference_id', 'created_at')
    list_filter = ('transaction_type',)
    search_fields = ('wallet__user__username', 'reference_id')
