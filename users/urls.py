from django.urls import path
from . import views

urlpatterns = [
    path("me", views.Me.as_view(), name="user_me"),
    path("log-in", views.LogIn.as_view(), name="user_login"),
    path("log-out", views.LogOut.as_view(), name="user_logout"),
    path("sign-up", views.SignUp.as_view(), name="user_signup"),
    path(
        "change-password", views.ChangePassword.as_view(), name="user_change_password"
    ),
    path("<int:pk>", views.PublicUser.as_view(), name="user_public_profile"),
    path("validate-email", views.EmailCheck.as_view(), name="check_email_exists"),
    path("validate-phone", views.PhoneNumberCheck.as_view(), name="check_phone_exists"),
    # path("jwt-login", views.JWTLogIn.as_view()),
]
