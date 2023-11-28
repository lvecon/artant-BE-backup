from django.urls import path
from .views import (
    UserFavoriteProducts,
    FavoriteProductToggle,
    UserFavoriteShops,
    FavoriteShopToggle,
)

urlpatterns = [
    path("products/user/<int:user_pk>", UserFavoriteProducts.as_view()),
    path("products/<int:product_pk>", FavoriteProductToggle.as_view()),
    path("shops/user/<int:user_pk>", UserFavoriteShops.as_view()),
    path("shops/<int:shop_pk>", FavoriteShopToggle.as_view()),
]
