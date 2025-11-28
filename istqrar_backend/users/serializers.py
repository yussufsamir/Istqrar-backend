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
    national_id_image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'national_id_image']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        national_id_image = validated_data.pop('national_id_image', None)
        
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.password = make_password(validated_data['password'])

        if national_id_image:
            user.national_id_image = national_id_image

        user.save()

        # Create profile ONLY IF it does not already exist
        Profile.objects.get_or_create(user=user)

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
