from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import FavoriteProduct
from shops.models import Shop
from products.models import Product


class FavoriteProductSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    discount_rate = serializers.SerializerMethodField()
    is_star_seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "shop_name",
            "original_price",
            "price",
            "discount_rate",
            "free_shipping",
            "is_discount",
            "is_best_seller",
            "is_star_seller",
            "is_liked",
            "thumbnail",
            "category",
        )

    def get_is_liked(self, product):
        request = self.context.get("request")

        if request:
            if request.user.is_authenticated:
                return FavoriteProduct.objects.filter(
                    user=request.user,
                    products__pk=product.pk,  # 이 부분을 수정하여 products 필드의 pk를 확인합니다.
                ).exists()
        return False

    def get_category(self, product):
        return product.category.get(level=2).name

    def get_shop_name(self, product):
        return product.shop.shop_name

    def get_discount_rate(self, product):
        if product.original_price & product.price:
            return int((1 - product.price / product.original_price) * 100)
        else:
            return 0

    def get_is_star_seller(self, product):
        return product.shop.is_star_seller


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
