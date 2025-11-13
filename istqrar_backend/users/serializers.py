from rest_framework import serializers
from .models import User, Profile, TrustScore
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number',
            'national_id', 'role', 'verified'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class TrustScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustScore
        fields = '__all__'
