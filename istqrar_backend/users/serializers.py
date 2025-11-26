from rest_framework import serializers
from .models import User, Profile, TrustScore
from django.contrib.auth.hashers import make_password
from startup.models import Mentor


class UserSerializer(serializers.ModelSerializer):
    trust_score = serializers.DecimalField(
        source='trust_score.score',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number',
            'national_id', 'role', 'verified', 'trust_score'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password','role']
        extra_kwargs = {'password': {'write_only': True},
                        'role': {'default': 'USER'}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.password = make_password(password)
        user.save()

        # Auto-create Mentor profile if role is mentor
        if user.role == "MENTOR":
            Mentor.objects.create(user=user, expertise="", bio="")

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class TrustScoreSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TrustScore
        fields = ['score', 'last_updated', 'user_username']
