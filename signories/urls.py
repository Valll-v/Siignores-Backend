from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from users.views import CustomUserViewSet
from rest_framework.routers import DefaultRouter


users = DefaultRouter()
users.register("users", CustomUserViewSet, basename='users')

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
   re_path(r'^auth/', include('djoser.urls.authtoken')),
]   
