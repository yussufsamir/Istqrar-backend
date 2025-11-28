from django.contrib import admin
from .models import User, Profile, TrustScore

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'verified')
    list_filter = ('role', 'verified')
    search_fields = ('username', 'email')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'income_range', 'date_of_birth')
    search_fields = ('user__username',)

@admin.register(TrustScore)
class TrustScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'last_updated')
    search_fields = ('user__username',)
