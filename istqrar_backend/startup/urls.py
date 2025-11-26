from rest_framework.routers import DefaultRouter
from .views import MentorViewSet, GrantApplicationViewSet

router = DefaultRouter()
router.register('mentors', MentorViewSet)
router.register('grants', GrantApplicationViewSet)

urlpatterns = router.urls
