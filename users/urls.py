from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create your views here.
urlpatterns = [
    path("", views.Users.as_view()),
    path("me", views.Me.as_view()),
    path("change-password", views.ChangePassword.as_view()),
    path("log-in", views.LogIn.as_view()),
    path("log-out", views.LogOut.as_view()),
    path("<int:pk>", views.PublicUser.as_view()),
    path("sign-up", views.SignUp.as_view(), name="signup"),
]
