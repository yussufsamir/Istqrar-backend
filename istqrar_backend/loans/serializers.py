from .models import *
from rest_framework import serializers

class LoanSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Loan
        fields = [
            'id', 'user', 'user_username',
            'amount', 'purpose', 'status',
            'created_at', 'approved_at',
            'due_date', 'interest_rate'
        ]

class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Repayment
        fields = "__all__"