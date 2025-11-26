from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterView
from django.urls import path, include

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]
