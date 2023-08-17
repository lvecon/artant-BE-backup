from django.urls import path
from .views import (
    FavoritesItems,
    UserFavoritesItems,
    FavoriteItemToggle,
    FavoritesShops,
    UserFavoritesShops,
    FavoriteShopToggle,
)

urlpatterns = [
    path("items", FavoritesItems.as_view()),
    path("items/<int:pk>", UserFavoritesItems.as_view()),
    path("items/toggle/<int:product_pk>", FavoriteItemToggle.as_view()),
    path("shops", FavoritesShops.as_view()),
    path("shops/<int:pk>", UserFavoritesShops.as_view()),
    path("shops/toggle/<int:shop_pk>", FavoriteShopToggle.as_view()),
]
