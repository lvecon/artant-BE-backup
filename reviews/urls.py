from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create your views here.
urlpatterns = [
    path("<int:pk>", views.ReviewDetails.as_view()),
]
