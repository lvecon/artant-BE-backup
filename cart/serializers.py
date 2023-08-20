from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Cart, CartLine
from products.serializers import ProductListSerializer, VariantValueSerializer
from users.serializers import TinyUserSerializer


class CartLineSerializer(ModelSerializer):
    product = ProductListSerializer()
    variant = VariantValueSerializer(many=True, read_only=True)
    count_in_other_carts = serializers.SerializerMethodField()

    class Meta:
        model = CartLine
        fields = ("product", "variant", "quantity", "count_in_other_carts")

    def get_count_in_other_carts(self, cart_line):
        product = cart_line.product

        count_in_other_carts = CartLine.objects.filter(
            product=product,
        ).count()

        return count_in_other_carts


class CartSerializer(ModelSerializer):
    cartline = CartLineSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("cartline",)
