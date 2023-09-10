from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Cart, CartLine
from products.serializers import (
    ProductListSerializer,
    VariantValueSerializer,
    ProductDetailSerializer,
)
from users.serializers import TinyUserSerializer


class CartLineSerializer(ModelSerializer):
    product = ProductDetailSerializer()
    variant = VariantValueSerializer(many=True, read_only=True)
    count_in_carts = serializers.SerializerMethodField()

    class Meta:
        model = CartLine
        fields = (
            "pk",
            "product",
            "variant",
            "quantity",
            "count_in_carts",
        )

    def get_count_in_carts(self, cart_line):
        product = cart_line.product

        count_in_carts = CartLine.objects.filter(
            product=product,
        ).count()

        return count_in_carts


class CartSerializer(ModelSerializer):
    cartline = CartLineSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("cartline",)
