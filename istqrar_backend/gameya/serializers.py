from rest_framework import serializers
from .models import Gameya, Membership, Contribution

class GameyaSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)

    class Meta:
        model = Gameya
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'creator_username', 'total_members', 'current_round', 'created_at']



class MembershipSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    gameya_name = serializers.CharField(source='gameya.name', read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id',
            'user',
            'user_username',
            'gameya',
            'gameya_name',
            'joined_at',
            'is_active',
            'payout_order',
        ]


class ContributionSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='membership.user.username', read_only=True)
    gameya_id = serializers.IntegerField(source='membership.gameya.id', read_only=True)

    class Meta:
        model = Contribution
        fields = [
            'id',
            'membership',
            'member_username',
            'gameya_id',
            'amount',
            'month',
            'paid_at',
            'confirmed',
        ]
