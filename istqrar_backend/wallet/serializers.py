from rest_framework import serializers
from .models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'user_username', 'balance', 'last_updated']


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='wallet.user.username', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'wallet', 'user',
            'transaction_type', 'amount',
            'reference_id', 'description',
            'created_at'
        ]
