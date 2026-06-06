from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from common.views import request_stats
from common.cron_views import trigger_reminders

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/notes/", include("notes.urls")),
    path("api/labels/", include("labels.urls")),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/stats/requests/", request_stats, name="request-stats"),
    path("api/chatbot/", include("chatbot.urls")),
    path("api/cron/trigger-reminders/", trigger_reminders, name="cron-trigger-reminders"),
    path("api/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]), name="swagger-ui"),
]
