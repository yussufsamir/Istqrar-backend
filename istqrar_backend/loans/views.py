from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from .models import Loan, Repayment
from .serializers import LoanSerializer, RepaymentSerializer
from wallet.models import Wallet, Transaction
from users.utils import update_trust_score


class LoanViewset(viewsets.ModelViewSet):
    queryset = Loan.objects.all().order_by('-created_at')
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Loan.objects.all().order_by('-created_at')
        return Loan.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        trust_score = self.request.user.trust_score.score
        if trust_score < 60:
            raise ValidationError({"detail": "Your trust score is too low to apply for a loan."})

        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        loan = self.get_object()

        if loan.status != 'PENDING':
            return Response({'detail': 'Loan is already processed.'}, status=status.HTTP_400_BAD_REQUEST)

        due_date = request.data.get('due_date')
        interest_rate = request.data.get('interest_rate')

        if interest_rate is not None:
            try:
                loan.interest_rate = Decimal(str(interest_rate))
            except:
                return Response({"detail": "Invalid interest_rate."}, status=status.HTTP_400_BAD_REQUEST)

        if due_date:
            loan.due_date = due_date

        wallet, _ = Wallet.objects.get_or_create(user=loan.user)
        wallet.balance = wallet.balance + loan.amount
        wallet.save()

        Transaction.objects.create(
            wallet=wallet,
            transaction_type='LOAN_DISBURSE',
            amount=loan.amount,
            reference_id=f"LOAN-{loan.id}",
            description=f"Loan disbursement for Loan #{loan.id}"
        )

        loan.status = 'APPROVED'
        loan.approved_at = timezone.now()
        loan.save()

        return Response(LoanSerializer(loan).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        loan = self.get_object()
        if loan.status != 'PENDING':
            return Response({'detail': 'Loan is already processed.'}, status=status.HTTP_400_BAD_REQUEST)

        loan.status = 'REJECTED'
        loan.save()

        return Response({"detail": "Loan rejected."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def repay(self, request, pk=None):
        loan = self.get_object()

        if loan.user != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response({'detail': 'You can only repay your own loans.'}, status=status.HTTP_403_FORBIDDEN)

        if loan.status == 'PAID':
            return Response({'detail': 'This loan is already fully paid.'}, status=status.HTTP_400_BAD_REQUEST)

        if loan.status != 'APPROVED':
            return Response({'detail': 'Only approved loans can be repaid.'}, status=status.HTTP_400_BAD_REQUEST)

        amount = request.data.get('amount')
        if not amount:
            return Response({'detail': 'Repayment amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(amount))
        except:
            return Response({"detail": "Amount must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'detail': 'Repayment amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)

        wallet, _ = Wallet.objects.get_or_create(user=loan.user)

        if wallet.balance < amount:
            return Response({'detail': 'Insufficient wallet balance.'}, status=status.HTTP_400_BAD_REQUEST)

        # FIXED TYPO HERE
        wallet.balance = wallet.balance - amount
        wallet.save()

        Transaction.objects.create(
            wallet=wallet,
            transaction_type='LOAN_REPAY',
            amount=amount,
            reference_id=f"LOAN-{loan.id}",
            description=f"Loan repayment for Loan #{loan.id}"
        )

        Repayment.objects.create(
            loan=loan,
            amount=amount,
            is_paid=True,
            payment_date=timezone.now()
        )

        # Recalculate totals
        serializer = LoanSerializer(loan)
        total_due = Decimal(str(serializer.data['total_due']))
        total_repaid = Decimal(str(serializer.data['total_repaid']))

        if total_repaid >= total_due:
            loan.status = 'PAID'
            loan.save()

        # TRUST SCORE REWARD
        update_trust_score(request.user, +10)

        return Response(
            {
                "detail": "Repayment successful.",
                "loan": LoanSerializer(loan).data,
            },
            status=status.HTTP_200_OK
        )
