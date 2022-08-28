from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
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
   re_path(r'^courses/', include(courses.urls)),
   path('courses/course/get_modules<int:course_id>/', CourseViewSet.as_view({'get': 'get_modules'})),
   re_path(r"^auth/token/login/?$", CustomTokenCreateView.as_view(), name="login"),
   path(r'app/', ApplicationView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
