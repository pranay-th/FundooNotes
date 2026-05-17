from django.urls import path

from .views import (
    register,
    login,
    logout,
    profile,
    reset_password_request,
    reset_password_confirm,
    verify_email,
)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("profile/", profile, name="profile"),
    path("reset-password/", reset_password_request, name="reset-password"),
    path("reset-password-confirm/", reset_password_confirm, name="reset-password-confirm"),
    path("verify-email/", verify_email, name="verify-email"),
]
