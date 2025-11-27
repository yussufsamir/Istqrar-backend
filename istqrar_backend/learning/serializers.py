from rest_framework import serializers
from .models import Course, Lesson, Certificate, Enrollment, CompletedLesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id',
            'course',
            'title',
            'content',
            'video_url',
            'order'
        ]


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'duration',
            'created_at',
            'lessons'
        ]


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id',
            'user',
            'username',
            'course',
            'course_title',
            'issued_at'
        ]
        read_only_fields = ['issued_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'username', 'course', 'course_title', 'enrolled_at']
        read_only_fields = ['user', 'enrolled_at']

class CompletedLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedLesson
        fields = '__all__'
