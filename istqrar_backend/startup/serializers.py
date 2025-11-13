from rest_framework import serializers
from .models import Mentor, GrantApplication


class MentorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Mentor
        fields = '__all__'


class GrantApplicationSerializer(serializers.ModelSerializer):
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    mentor_username = serializers.CharField(source='mentor.user.username', read_only=True, default=None)

    class Meta:
        model = GrantApplication
        fields = '__all__'
