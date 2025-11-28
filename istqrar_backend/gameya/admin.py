from django.contrib import admin
from .models import Gameya, Membership, Contribution

@admin.register(Gameya)
class GameyaAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'contribution_amount', 'duration_months', 'total_members', 'current_round', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'creator__username')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'gameya', 'payout_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'gameya__name')

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('membership', 'amount', 'month', 'confirmed', 'paid_at')
    list_filter = ('confirmed',)
    search_fields = ('membership__user__username',)
