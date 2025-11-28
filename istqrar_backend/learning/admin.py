from django.contrib import admin
from .models import Course, Lesson, Certificate, Enrollment, CompletedLesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'created_at')
    search_fields = ('title',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'issued_at')
    search_fields = ('user__username',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    search_fields = ('user__username',)

@admin.register(CompletedLesson)
class CompletedLessonAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed_at')
    search_fields = ('user__username',)
