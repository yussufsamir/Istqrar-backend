from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from decimal import Decimal
from django.db import transaction
from users.utils import update_trust_score
from .models import Gameya, Membership, Contribution
from .serializers import GameyaSerializer, MembershipSerializer, ContributionSerializer
from wallet.models import Wallet, Transaction
# Create your views here.

class IsCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user or request.user.is_superuser

class GameyaViewSet(viewsets.ModelViewSet):
    queryset=Gameya.objects.all().order_by('-created_at')
    serializer_class=GameyaSerializer
    permission_classes= [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, total_members=0, current_round=1)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        gameya = self.get_object()

        if gameya.max_members and gameya.total_members >= gameya.max_members:
            return Response({'detail': 'This Gameya is full.'}, status=status.HTTP_400_BAD_REQUEST)
        
        membership, created = Membership.objects.get_or_create(
            user=request.user,
            gameya=gameya,
            defaults={'is_active': True,
                      'payout_order': gameya.total_members + 1}
        )
        if not created and membership.is_active:
            return Response({'detail': 'You have already joined this Gameya.'}, status=status.HTTP_400_BAD_REQUEST)
        if not created:
            membership.is_active = True
            membership.save()

        gameya.total_members = gameya.memberships.filter(is_active=True).count()
        gameya.save()

        return Response(
            MembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def leave(self,request,pk=None):
        gameya=self.get_object()
        try:
            membership=Membership.objects.get(user=request.user,gameya=gameya,is_active=True)
        except Membership.DoesNotExist:
            return Response({'detail':'You are not an active member of this Gameya.'},status=status.HTTP_400_BAD_REQUEST)
        membership.is_active=False
        membership.save()
        gameya.total_members=gameya.memberships.filter(is_active=True).count()
        gameya.save()
        update_trust_score(request.user, -10)
        return Response({'detail':'You have left the Gameya.'},status=status.HTTP_200_OK)
    
        @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
        def contribute(self, request, pk=None):
            gameya = self.get_object()

            # Check active membership
            try:
                membership = Membership.objects.get(user=request.user, gameya=gameya, is_active=True)
            except Membership.DoesNotExist:
                return Response(
                    {"detail": "You are not an active member of this Gameya."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            wallet, _ = Wallet.objects.get_or_create(user=request.user)

            amount = gameya.contribution_amount
            month = request.data.get("month", gameya.current_round)

            # Prevent duplicate contribution
            if Contribution.objects.filter(
                membership=membership,
                month=month,
                confirmed=True
            ).exists():
                return Response(
                    {"detail": "You have already contributed for this month."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check wallet balance
            if wallet.balance < amount:
                return Response(
                    {"detail": "Insufficient wallet balance."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Atomic transaction block
            with transaction.atomic():

                # Deduct funds
                wallet.balance = wallet.balance - amount
                wallet.save()

                # Log transaction
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type="CONTRIBUTION",
                    amount=amount,
                    reference_id=f"GAMEYA-{gameya.id}-ROUND-{month}",
                    description=f"Contribution for Gameya {gameya.name}, month {month}",
                )

                # Create contribution record
                contribution = Contribution.objects.create(
                    membership=membership,
                    amount=amount,
                    month=month,
                    confirmed=True,
                )

            # Increase trust score for successful payment
            update_trust_score(request.user, +5)

            return Response(
                ContributionSerializer(contribution).data,
                status=status.HTTP_201_CREATED
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def payout(self, request, pk=None):
        gameya = self.get_object()
        if gameya.creator != request.user and not request.user.is_superuser:
            return Response(
                {"detail": "Only the Gameya creator or admin can trigger payout."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            target_membership = Membership.objects.get(
                gameya=gameya,
                payout_order=gameya.current_round,
                is_active=True
            )
        except Membership.DoesNotExist:
            return Response(
                {"detail": "No active member found for the current payout order."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        active_members=gameya.memberships.filter(is_active=True).count()
        pot=gameya.contribution_amount * Decimal(active_members)

        wallet, _ = Wallet.objects.get_or_create(user=target_membership.user)
        with transaction.atomic():
            wallet.balance = wallet.balance + pot
            wallet.save()

            Transaction.objects.create(
                wallet=wallet,
                transaction_type='PAYOUT',
                amount=pot,
                reference_id=f"GAMEYA-{gameya.id}-ROUND-{gameya.current_round}",
                description=f"Payout for Gameya {gameya.name}, round {gameya.current_round}",
            )

            # move to next round or complete
            if gameya.current_round >= gameya.duration_months:
                gameya.status = 'COMPLETED'
            else:
                gameya.current_round += 1
            gameya.save()

        return Response(
            {
                "detail": "Payout completed.",
                "round": gameya.current_round,
                "amount": pot,
                "beneficiary": target_membership.user.username,
            },
            status=status.HTTP_200_OK,
        )
    
class MembershipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Membership.objects.all().select_related('user', 'gameya')
    serializer_class=MembershipSerializer
    permission_classes=[permissions.IsAuthenticated]

class ContributionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Contribution.objects.all().select_related('membership', 'membership__user', 'membership__gameya')
    serializer_class=ContributionSerializer
    permission_classes=[permissions.IsAuthenticated]

    


