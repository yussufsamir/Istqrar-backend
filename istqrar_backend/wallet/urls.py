from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, TransactionViewSet, DepositView
router = DefaultRouter()
router.register('wallet', WalletViewSet, basename='wallet')
router.register('transactions', TransactionViewSet, basename='transactions')

deposit = DepositView.as_view({'post': 'add'})

urlpatterns = [
    # CUSTOM ROUTES FIRST
    path('wallet/deposit/', deposit, name='wallet-deposit'),

    # ROUTER ROUTES LAST
    path('', include(router.urls)),
]
