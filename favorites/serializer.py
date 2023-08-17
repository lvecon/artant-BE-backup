from rest_framework.serializers import ModelSerializer
from .models import FavoriteItem, FavoriteShop
from products.serializers import ProductListSerializer
from users.serializers import TinyShopSerializer


class TinyFavoriteItemSerializer(ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = (
            "user",
            "products",
        )


class FavoriteItemSerializer(ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = FavoriteItem
        fields = (
            "user",
            "products",
        )


class TinyFavoriteShopSerializer(ModelSerializer):
    class Meta:
        model = FavoriteShop
        fields = (
            "user",
            "shops",
        )


class FavoriteShopSerializer(ModelSerializer):
    shops = TinyShopSerializer(many=True, read_only=True)

    class Meta:
        model = FavoriteShop
        fields = (
            "user",
            "shops",
        )
