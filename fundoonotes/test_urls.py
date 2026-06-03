"""
test_urls.py — URL configuration for the test suite.

Only includes the users app URLs (notes and labels apps don't exist yet).
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
