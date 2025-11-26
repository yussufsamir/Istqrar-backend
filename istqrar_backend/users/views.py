from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileSerializer,
    TrustScoreSerializer,
)

from .models import User, Profile, TrustScore
from rest_framework.permissions import AllowAny

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - Admin can view all users
    - Normal users only see themselves
    - Includes /me/ and /trust_score/ endpoints
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all().order_by('id')
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Return logged-in user's profile + trust score."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def trust_score(self, request):
        """Return only the trust score."""
        trust = request.user.trust_score
        serializer = TrustScoreSerializer(trust)
        return Response(serializer.data)
    
