from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Cart, CartLine
from products.serializers import (
    TinyProductVariantSerializer,
    ProductSnapshotSerializer,
)


class CartLineSerializer(ModelSerializer):
    product_variant = TinyProductVariantSerializer(required=False, allow_null=True)
    product = ProductSnapshotSerializer()
    count_in_carts = serializers.SerializerMethodField()

    class Meta:
        model = CartLine
        fields = (
            "pk",
            "product",
            "product_variant",
            "quantity",
            "count_in_carts",
        )

    def get_count_in_carts(self, obj):
        # `product_variant`가 `None`일 때를 고려하여 처리
        if obj.product_variant:
            return CartLine.objects.filter(product_variant=obj.product_variant).count()
        else:
            return CartLine.objects.filter(product=obj.product).count()


class CartSerializer(ModelSerializer):
    shop_cartlines = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("shop_cartlines",)

    def get_shop_cartlines(self, obj):
        shop_to_cartlines = {}
        for cartline in obj.cartlines.all():
            shop = cartline.product.shop

            # 각 상점의 ID를 키로 사용하여 상점 정보를 딕셔너리에 저장합니다.
            if shop.id not in shop_to_cartlines:
                shop_to_cartlines[shop.id] = {
                    "shop_id": shop.id,
                    "shop_name": shop.shop_name,
                    "shop_avatar": shop.avatar,
                    "cart_lines": [],
                }

            # CartLineSerializer를 사용하여 카트 라인 정보를 직렬화합니다.
            shop_cartline_data = CartLineSerializer(cartline).data
            # 해당 상점의 카트 라인 리스트에 추가합니다.
            shop_to_cartlines[shop.id]["cart_lines"].append(shop_cartline_data)

        return list(shop_to_cartlines.values())
