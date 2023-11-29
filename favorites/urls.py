from django.urls import path
from .views import (
    UserFavoritesProducts,
    FavoriteProductToggle,
    UserFavoritesShops,
    FavoriteShopToggle,
)

urlpatterns = [
    path("products/user/<int:user_pk>", UserFavoritesProducts.as_view()),
    path("products/<int:product_pk>", FavoriteProductToggle.as_view()),
    path("shops/user/<int:user_pk>", UserFavoritesShops.as_view()),
    path("shops/<int:shop_pk>", FavoriteShopToggle.as_view()),
]
