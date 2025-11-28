from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from users.models import TrustScore
from gameya.models import Gameya, Membership, Contribution
from loans.models import Loan
from wallet.models import Transaction


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # --- TRUST SCORE ---
        trust_score = None
        if hasattr(user, 'trust_score'):
            trust_score = float(user.trust_score.score)

        # --- ACTIVE GAMEYA ---
        my_memberships = Membership.objects.filter(user=user, is_active=True)
        active_gameya = None

        if my_memberships.exists():
            g = my_memberships[0].gameya  # one active for now
            active_gameya = {
                "id": g.id,
                "name": g.name,
                "contribution_amount": float(g.contribution_amount),
                "current_round": g.current_round,
                "duration_months": g.duration_months,
                "next_payout_date": g.get_next_payout_date(),
                "progress": round((g.current_round / g.duration_months) * 100, 2),
            }

        # --- ACTIVE LOAN ---
        active_loan = None
        loan = Loan.objects.filter(user=user, status="APPROVED").first()

        if loan:
            total_due = loan.amount + (loan.amount * (loan.interest_rate / 100))
            repayments_sum = sum((r.amount for r in loan.repayments.filter(is_paid=True)), 0)

            active_loan = {
                "id": loan.id,
                "amount": float(loan.amount),
                "interest_rate": float(loan.interest_rate),
                "total_due": float(total_due),
                "total_repaid": float(repayments_sum),
                "remaining": float(total_due - repayments_sum),
                "progress": round((repayments_sum / total_due) * 100, 2),
                "next_payment_date": loan.due_date
            }

        # --- RECENT TRANSACTIONS ---
        transactions = Transaction.objects.filter(wallet__user=user).order_by('-created_at')[:5]
        recent_transactions = [
            {
                "type": t.transaction_type,
                "amount": float(t.amount),
                "date": t.created_at,
                "description": t.description,
            }
            for t in transactions
        ]

        return Response({
            "trust_score": trust_score,
            "active_gameya": active_gameya,
            "active_loan": active_loan,
            "recent_transactions": recent_transactions
        })
