from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from datetime import timedelta
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
            return Response({'detail': 'Loan already processed.'}, status=400)

        # interest override
        interest_rate = request.data.get("interest_rate")
        if interest_rate:
            loan.interest_rate = Decimal(str(interest_rate))

        # auto-set due date based on repayment period (3,6,12 months)
        months = loan.repayment_period
        loan.due_date = timezone.now().date() + timedelta(days=30 * months)

        # disburse to wallet
        wallet, _ = Wallet.objects.get_or_create(user=loan.user)
        wallet.balance += loan.amount
        wallet.save()

        Transaction.objects.create(
            wallet=wallet,
            transaction_type='LOAN_DISBURSE',
            amount=loan.amount,
            reference_id=f"LOAN-{loan.id}",
            description=f"Loan disbursement"
        )

        loan.status = "APPROVED"
        loan.approved_at = timezone.now()
        loan.save()

        return Response(LoanSerializer(loan).data, status=200)

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

        # Only loan owner or admin can repay
        if loan.user != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response({'detail': 'You can only repay your own loans.'}, status=403)

        if loan.status != 'APPROVED':
            return Response({'detail': 'Only approved loans can be repaid.'}, status=400)

        # Get repayment amount
        amount = request.data.get('amount')
        if not amount:
            return Response({'detail': 'Repayment amount is required.'}, status=400)

        try:
            amount = Decimal(str(amount))
        except:
            return Response({'detail': 'Invalid amount.'}, status=400)

        if amount <= 0:
            return Response({'detail': 'Repayment amount must be positive.'}, status=400)

        # Wallet check
        wallet, _ = Wallet.objects.get_or_create(user=loan.user)
        if wallet.balance < amount:
            return Response({'detail': 'Insufficient wallet balance.'}, status=400)

        # Calculate totals before repaying
        serializer = LoanSerializer(loan)
        total_due = Decimal(str(serializer.data['total_due']))
        total_repaid = Decimal(str(serializer.data['total_repaid']))
        remaining = total_due - total_repaid

        # ❗ NEW: Prevent overpayment
        if amount > remaining:
            return Response({"detail": "You cannot repay more than the remaining loan amount."}, status=400)

        # Deduct from wallet
        wallet.balance = wallet.balance - amount
        wallet.save()

        # Log transaction
        Transaction.objects.create(
            wallet=wallet,
            transaction_type='LOAN_REPAY',
            amount=amount,
            reference_id=f"LOAN-{loan.id}",
            description=f"Loan repayment for Loan #{loan.id}"
        )

        # Create repayment record
        Repayment.objects.create(
            loan=loan,
            amount=amount,
            is_paid=True,
            payment_date=timezone.now()
        )

        # Recalculate repayment totals AFTER payment
        serializer = LoanSerializer(loan)
        total_repaid = Decimal(str(serializer.data['total_repaid']))
        total_due = Decimal(str(serializer.data['total_due']))

        if total_repaid >= total_due:
            loan.status = 'PAID'
            loan.save()
            update_trust_score(request.user, +20)  # Reward for finishing loan
        else:
            update_trust_score(request.user, +5)   # Reward for each payment

        return Response({
            "detail": "Repayment successful.",
            "loan": LoanSerializer(loan).data
        }, status=200)


    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def active(self, request):
        user = request.user

        # Find the active loan
        loan = Loan.objects.filter(
            user=user,
            status="APPROVED"
        ).first()

        if not loan:
            return Response({"detail": "No active loan."}, status=200)

        # Calculate repayment stats
        repayments = loan.repayments.filter(is_paid=True)
        total_repaid = sum([r.amount for r in repayments])
        total_due = loan.amount + (loan.amount * loan.interest_rate / 100)

        # Fake next payment date (until we implement real schedule)
        next_payment_date = None
        if loan.due_date:
            next_payment_date = loan.due_date

        data = {
            "loan_id": loan.id,
            "amount": str(loan.amount),
            "interest_rate": str(loan.interest_rate),
            "total_due": str(total_due),
            "total_repaid": str(total_repaid),

            "progress_text": f"{total_repaid} / {total_due}",

            "progress_percent": round((total_repaid / total_due) * 100, 2) if total_due > 0 else 0,

            "next_payment_date": next_payment_date,
            "status": loan.status,
            "purpose": loan.purpose,
        }

        return Response(data, status=200)
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def history(self, request):
        user = request.user

        # Get user's completed loans
        loans = Loan.objects.filter(
            user=user,
            status='PAID'
        ).order_by('-approved_at')

        results = []

        for loan in loans:
            repayments = loan.repayments.filter(is_paid=True)
            total_repaid = sum([r.amount for r in repayments])

            # Paid date → last repayment date
            paid_on = None
            if repayments.exists():
                paid_on = repayments.latest('payment_date').payment_date

            results.append({
                "loan_id": loan.id,
                "amount": str(loan.amount),
                "purpose": loan.purpose,
                "total_repaid": str(total_repaid),
                "paid_on": paid_on,
            })

        return Response(results, status=200)
