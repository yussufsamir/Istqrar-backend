from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonViewSet, EnrollmentViewSet, CertificateViewSet

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='courses')
router.register('lessons', LessonViewSet, basename='lessons')
router.register('enrollments', EnrollmentViewSet, basename='enrollments')
router.register('certificates', CertificateViewSet, basename='certificates')

urlpatterns = [
    path('', include(router.urls)),
    path('enrolled/', EnrollmentViewSet.as_view({'get': 'my_enrollments'}), name='my-enrollments'),
]
