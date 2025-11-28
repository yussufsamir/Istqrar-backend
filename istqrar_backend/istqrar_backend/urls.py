from django.urls import path, include
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

from dashboard.views import DashboardView




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('users.urls')), 
    path('api/', include('gameya.urls')),     
    path('api/', include('wallet.urls')),
    path('api/', include('loans.urls')),
    path('api/startup/', include('startup.urls')),
    path('api/learning/', include('learning.urls')),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
