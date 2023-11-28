from django.urls import path
from .views import (
    UserFavoritesItems,
    FavoriteItemToggle,
    UserFavoritesShops,
    FavoriteShopToggle,
)

urlpatterns = [
    path("products/user/<int:user_pk>", UserFavoritesItems.as_view()),
    path("products/toggle/<int:product_pk>", FavoriteItemToggle.as_view()),
    path("shops/user/<int:user_pk>", UserFavoritesShops.as_view()),
    path("shops/toggle/<int:shop_pk>", FavoriteShopToggle.as_view()),
]
