from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("me", views.Me.as_view(), name="user_me"),
    path("log-in", views.LogIn.as_view(), name="user_login"),
    path("log-out", views.LogOut.as_view(), name="user_logout"),
    path("sign-up", views.SignUp.as_view(), name="user_signup"),
    path(
        "change-password", views.ChangePassword.as_view(), name="user_change_password"
    ),
    path("<int:pk>", views.PublicUser.as_view(), name="user_public_profile"),
    path(
        "validate-corporate-number",
        views.CorporateNumberCheck.as_view(),
        name="check_corporate_number",
    ),
    path("validate-email", views.EmailCheck.as_view(), name="check_email_exists"),
    path("validate-phone", views.PhoneNumberCheck.as_view(), name="check_phone_exists"),
    path("kakao", views.KakaoLogIn.as_view(), name="kakao_login"),
    path(
        "request-password-reset",
        views.PasswordResetRequestView.as_view(),
        name="request_password_reset",
    ),
    path(
        "password-reset-confirm",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # path("jwt-login", views.JWTLogIn.as_view()),
]
