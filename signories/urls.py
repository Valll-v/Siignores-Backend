from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from applications.views import ApplicationView
from courses.views import CourseViewSet
from users.views import CustomUserViewSet, CustomTokenCreateView
from rest_framework.routers import DefaultRouter

users = DefaultRouter()
users.register("users", CustomUserViewSet, basename='users')

courses = DefaultRouter()
courses.register("course", CourseViewSet, basename='users')

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
   path('admin/', admin.site.urls),
   re_path(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   #  re_path(r'^auth/', include('djoser.urls')),
   re_path(r'^auth/', include(users.urls)),
   re_path(r'', include(courses.urls)),
   path('course/course_students/<int:course_id>/', CourseViewSet.as_view({'get': 'course_students'})),
   path('course/get_modules/<int:course_id>/', CourseViewSet.as_view({'get': 'get_modules'})),
   path('course/get_lessons/<int:module_id>/', CourseViewSet.as_view({'get': 'get_lessons'})),
   path('course/course/<int:course_id>/', CourseViewSet.as_view({'get': 'course_get', 'delete': 'course_del'})),
   path('course/module/<int:module_id>/', CourseViewSet.as_view({'get': 'module_get', 'delete': 'module_del'})),
   path('course/lesson/<int:lesson_id>/', CourseViewSet.as_view({'get': 'lesson_get', 'delete': 'lesson_del'})),
   path('course/special/<int:special_id>/', CourseViewSet.as_view({'get': 'special_get', 'delete': 'special_del'})),
   path('course/student/<int:student_id>/', CourseViewSet.as_view({'get': 'student'})),
   path('course/timer/<int:lesson_id>/', CourseViewSet.as_view({'post': 'add_timer'})),
   path('course/file/<int:lesson_id>/', CourseViewSet.as_view({'post': 'add_files'})),
   path('course/timer_del/<int:timer_id>/', CourseViewSet.as_view({'delete': 'delete_timer'})),
   path('course/file_del/<int:file_id>/', CourseViewSet.as_view({'delete': 'delete_file'})),
   path('course/homework_by_course/<int:course_id>/', CourseViewSet.as_view({'get': 'get_all_homework_by_course'})),
   path('course/homework_by_module/<int:module_id>/', CourseViewSet.as_view({'get': 'get_all_homework_by_module'})),
   path('course/homework_by_lesson/<int:lesson_id>/', CourseViewSet.as_view({'get': 'get_all_homework_by_lesson'})),
   path('course/target_homework/<int:homework_id>/', CourseViewSet.as_view({'get': 'get_target_homework'})),
   path('course/calendar/<int:calendar_id>/', CourseViewSet.as_view({'get': 'get_calendar',
                                                                     'delete': 'delete_calendar'})),
   path("auth/users/app_users/<int:app_id>/", CustomUserViewSet.as_view({'get': 'get_users'}), name="login"),
   path('users/', CustomUserViewSet.as_view({'delete': 'delete'})),
   re_path(r"^auth/token/login/?$", CustomTokenCreateView.as_view(), name="login"),
   path(r'app/', ApplicationView.as_view()),
   path('chat/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
