from rest_framework import serializers
from .models import Loan, Repayment
from decimal import Decimal

class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = '__all__'
        read_only_fields = ['id', 'payment_date', 'is_paid']


class LoanSerializer(serializers.ModelSerializer):
    repayments = RepaymentSerializer(many=True, read_only=True)
    total_repaid = serializers.SerializerMethodField()
    total_due = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = '__all__'
        read_only_fields = [
            'id', 'user', 'status', 'created_at', 'approved_at'
        ]

    def get_total_repaid(self, obj):
        return sum((r.amount for r in obj.repayments.filter(is_paid=True)), Decimal('0'))

    def get_total_due(self, obj):
        amount = obj.amount
        interest = amount * (obj.interest_rate / Decimal('100'))
        return amount + interest

    def get_remaining_amount(self, obj):
        return self.get_total_due(obj) - self.get_total_repaid(obj)
