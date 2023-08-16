from django.urls import path
from .views import FavoritesItems

urlpatterns = [
    path("/1", FavoritesItems.as_view()),
]
