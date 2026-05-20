from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Users app
    path("api/users/", include("users.urls")),

    # Notes app
    path("api/notes/", include("notes.urls")),

    # Labels app
    path("api/labels/", include("labels.urls")),

    # JWT token refresh
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # API schema and docs (drf-spectacular) — publicly accessible
    path("api/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]), name="swagger-ui"),
]
