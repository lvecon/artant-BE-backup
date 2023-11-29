from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import FavoriteProduct
from shops.models import Shop
from products.serializers import ProductListSerializer


class FavoriteProductSerializer(ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = FavoriteProduct
        fields = (
            "user",
            "products",
        )


# 팔로우한 shop 정보
class FavoriteShopSerializer(ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = (
            "pk",
            "shop_name",
            "avatar",
            "thumbnails",
        )

    # 상점의 최대 4개 상품 썸네일
    def get_thumbnails(self, shop):
        thumbnails = shop.products.all()[:4].values_list("thumbnail", flat=True)
        return list(thumbnails)
