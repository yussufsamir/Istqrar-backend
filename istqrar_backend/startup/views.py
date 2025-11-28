from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import GrantApplication, Mentor , Article
from .serializers import GrantApplicationSerializer, MentorSerializer, ArticleSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

# Create your views here.
class MentorViewSet(viewsets.ModelViewSet):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GrantApplicationViewSet(viewsets.ModelViewSet):
    queryset = GrantApplication.objects.all().order_by('-submitted_at')
    serializer_class = GrantApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'ADMIN' or user.role == 'MENTOR':
            return GrantApplication.objects.all().order_by('-submitted_at')
        return GrantApplication.objects.filter(applicant=user).order_by('-submitted_at')
    
        if hasattr(user, 'mentor_profile'):
            mentor = user.mentor_profile
            return GrantApplication.objects.filter(mentor=mentor)
        
        return GrantApplication.objects.filter(applicant=user)
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def assign_mentor(self, request, pk=None):
        application = self.get_object()
        mentor_id = request.data.get('mentor_id')
        if not mentor_id :
            return Response({'detail': 'mentor_id is required.'}, status=400)

        try:
            mentor = Mentor.objects.get(id=mentor_id)
        except Mentor.DoesNotExist:
            return Response({'detail': 'Mentor not found.'}, status=404)

        application.mentor = mentor
        application.save()

        return Response({'detail': 'Mentor assigned successfully.'}, status=200)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        application = self.get_object()
        if application.status != 'PENDING':
            return Response({'detail': 'Application is already processed.'}, status=400)
        application.status = 'APPROVED'
        application.save()
        return Response({'detail': 'Application approved.'}, status=200)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        application= self.get_object()
        if application.status != 'PENDING':
            return Response({'detail': 'Application is already processed.'}, status=400)
        application.status = 'REJECTED'
        application.save()
        return Response({'detail': 'Application rejected.'}, status=200)
    
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        # Only admin can create/edit
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]