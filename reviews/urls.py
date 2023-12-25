from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>", views.ReviewDetails.as_view()),
]
