from django.contrib import admin
from .models import Mentor, GrantApplication

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise')
    search_fields = ('user__username',)

@admin.register(GrantApplication)
class GrantAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'applicant', 'mentor', 'status', 'amount_requested')
    list_filter = ('status',)
    search_fields = ('project_title', 'applicant__username')
