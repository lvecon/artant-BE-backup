from django.urls import path
from .views import (
    UserFavoritesProducts,
    FavoriteProductToggle,
    UserFavoritesShops,
    FavoriteShopToggle,
)

urlpatterns = [
    path(
        "products/user/<int:user_pk>",
        UserFavoritesProducts.as_view(),
        name="user_favorite_products",
    ),
    path(
        "products/<int:product_pk>",
        FavoriteProductToggle.as_view(),
        name="toggle_favorite_product",
    ),
    path(
        "shops/user/<int:user_pk>",
        UserFavoritesShops.as_view(),
        name="user_favorite_shops",
    ),
    path(
        "shops/<int:shop_pk>",
        FavoriteShopToggle.as_view(),
        name="toggle_favorite_shop",
    ),
]
