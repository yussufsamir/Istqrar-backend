from rest_framework import serializers
from .models import Mentor, GrantApplication


class MentorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Mentor
        fields = ['id', 'user', 'username', 'expertise', 'bio']
        read_only_fields = ['user']


class GrantApplicationSerializer(serializers.ModelSerializer):
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    mentor_username = serializers.CharField(source='mentor.user.username', read_only=True)

    class Meta:
        model = GrantApplication
        fields = [
            'id',
            'applicant', 'applicant_username',
            'mentor', 'mentor_username',
            'project_title', 'description',
            'amount_requested',
            'status', 'submitted_at'
        ]
        read_only_fields = ['applicant', 'status', 'submitted_at']
