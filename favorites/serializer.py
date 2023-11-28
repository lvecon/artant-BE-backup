from rest_framework.serializers import ModelSerializer
from .models import FavoriteProduct, FavoriteShop
from products.serializers import ProductListSerializer
from shops.serializers import ShopSerializer


class TinyFavoriteProductSerializer(ModelSerializer):
    class Meta:
        model = FavoriteProduct
        fields = (
            "user",
            "products",
        )


class FavoriteProductSerializer(ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = FavoriteProduct
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
    shops = ShopSerializer(many=True, read_only=True)

    class Meta:
        model = FavoriteShop
        fields = (
            "user",
            "shops",
        )
