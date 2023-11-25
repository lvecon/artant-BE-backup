from django.urls import path
from . import views


urlpatterns = [
    path("recently-viewed", views.RecentlyViewed.as_view()),
]
