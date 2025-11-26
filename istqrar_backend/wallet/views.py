from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer    
from rest_framework.decorators import action    
from rest_framework.response import Response
import decimal

# Create your views here.
class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        # Users should ONLY see their own wallet
        return Wallet.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)
    

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return Transaction.objects.filter(wallet=wallet).order_by('-timestamp')
    
class DepositView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def add(self, request):   
        amount = request.data.get("amount")

        if not amount:
            return Response({"detail": "Amount is required."}, status=400)

        amount = decimal.Decimal(amount)
        wallet, _ = Wallet.objects.get_or_create(user=request.user)

        wallet.balance += amount
        wallet.save()

        Transaction.objects.create(
            wallet=wallet,
            transaction_type='DEPOSIT',
            amount=amount,
            reference_id="WALLET-DEPOSIT",
            description="Wallet deposit"
        )

        return Response(
            {"detail": "Wallet topped up successfully", "balance": wallet.balance},
            status=200
        )
