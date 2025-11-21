from rest_framework.routers import DefaultRouter
from .views import GameyaViewSet , MembershipViewSet, ContributionViewSet   

router = DefaultRouter()
router.register(r'gameyas', GameyaViewSet, basename='gameya')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'contributions', ContributionViewSet, basename='contribution')

urlpatterns = router.urls
