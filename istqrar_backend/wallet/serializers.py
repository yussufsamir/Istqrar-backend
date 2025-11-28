from rest_framework import serializers
from .models import Wallet, Transaction

class WalletSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'user_username', 'balance']
        read_only_fields = ['user', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_type',
            'amount',
            'created_at',     
            'reference_id',
            'description',
        ]
