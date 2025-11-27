from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Course, Enrollment, Lesson, Certificate,CompletedLesson
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer, CertificateSerializer
from rest_framework import viewsets,permissions,status
# Create your views here.

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Only admin can create or update courses
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    @action(detail=True, methods=['get'])
    def enrolled_users(self, request, pk=None):
        if self.request.user.is_superuser == True or self.request.user.role == 'ADMIN':
            course = self.get_object()
            enrollments = Enrollment.objects.filter(course=course).select_related('user')

            data = [
                {
                    "user_id": e.user.id,
                    "username": e.user.username,
                    "enrolled_at": e.enrolled_at
                }
                for e in enrollments
            ]

            return Response(data)
        return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        course = self.get_object()
        total_lessons = course.lessons.count()

        completed = CompletedLesson.objects.filter(
            user=request.user,
            lesson__course=course
        ).count()

        percent = (completed / total_lessons * 100) if total_lessons else 0

        return Response({
            "course": course.title,
            "completed_lessons": completed,
            "total_lessons": total_lessons,
            "progress_percent": round(percent, 2)
        })
    
    @action(detail=True, methods=['post'])
    def issue_certificate(self, request, pk=None):
        course = self.get_object()

        total_lessons = course.lessons.count()
        completed = CompletedLesson.objects.filter(
            user=request.user, lesson__course=course
        ).count()

        if completed < total_lessons:
            return Response(
                {"detail": "You must complete all lessons before receiving a certificate."},
                status=400
            )

        if Certificate.objects.filter(user=request.user, course=course).exists():
            return Response({"detail": "Certificate already issued."}, status=400)

        cert = Certificate.objects.create(user=request.user, course=course)

        return Response({
            "detail": "Certificate issued.",
            "certificate_id": cert.id,
            "course": course.title
        }, status=201)


        
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all().order_by('order')
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Only admin can create or update lessons
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()  
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        lesson = self.get_object()

        # check if already completed
        if CompletedLesson.objects.filter(user=request.user, lesson=lesson).exists():
            return Response({"detail": "Lesson already completed."}, status=400)

        CompletedLesson.objects.create(user=request.user, lesson=lesson)

        return Response({"detail": "Lesson marked as completed."}, status=200)

    
class LearningProgressViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def complete_lesson(self, request):
        lesson_id = request.data.get("lesson_id")

        if not lesson_id:
            return Response(
                {"detail": "lesson_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Lesson not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user
        course = lesson.course

        # Session-based simple progress tracker
        key = f"course_{course.id}_completed_lessons"
        completed_lessons = request.session.get(key, [])

        if lesson_id in completed_lessons:
            return Response(
                {"detail": "Lesson already marked as completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add new completed lesson
        completed_lessons.append(lesson_id)
        request.session[key] = completed_lessons
        request.session.modified = True

        total_lessons = course.lessons.count()
        completed_count = len(completed_lessons)

        # If course is now complete → issue certificate
        if completed_count == total_lessons:
            # Issue certificate if not already issued
            if not Certificate.objects.filter(user=user, course=course).exists():
                Certificate.objects.create(user=user, course=course)
                

            return Response(
                {
                    "detail": "Course completed! Certificate issued.",
                    "course": course.title,
                    "completed_lessons": completed_count,
                    "total_lessons": total_lessons
                },
                status=status.HTTP_200_OK
            )

        # Normal lesson completion response
        return Response(
            {
                "detail": "Lesson completed.",
                "completed_lessons": completed_count,
                "total_lessons": total_lessons
            },
            status=status.HTTP_200_OK
        )

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.all().order_by('-issued_at')
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'ADMIN' :
            return Certificate.objects.all()
        return Certificate.objects.filter(user=user)
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all().order_by('-enrolled_at')
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_enrollments(self, request):
        enrollments = Enrollment.objects.filter(user=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'ADMIN' :
            return Enrollment.objects.all()
        return Enrollment.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
