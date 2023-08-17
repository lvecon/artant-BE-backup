from django.urls import path
from .views import (
    FavoritesItems,
    UserFavoritesItems,
    FavoritesShops,
    UserFavoritesShops,
)

urlpatterns = [
    path("items", FavoritesItems.as_view()),
    path("items/<int:pk>", UserFavoritesItems.as_view()),
    path("shops", FavoritesShops.as_view()),
    path("shops/<int:pk>", UserFavoritesShops.as_view()),
]
