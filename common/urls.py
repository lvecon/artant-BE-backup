from django.urls import path
from .views import GetUploadURL, GetVideoUploadURL

urlpatterns = [
    path("images/get-url", GetUploadURL.as_view()),
    path("videos/get-url", GetVideoUploadURL.as_view()),
]
