from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Purchase, PurchaseLine
from products.serializers import (
    ProductListSerializer,
    VariantValueSerializer,
    ProductDetailSerializer,
)
from users.serializers import TinyUserSerializer


class PurchaseLineSerializer(ModelSerializer):
    product = ProductDetailSerializer()
    variant = VariantValueSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseLine
        fields = (
            "pk",
            "product",
            "variant",
            "quantity",
            "order_date",
        )


class PurchaseSerializer(ModelSerializer):
    purchaseline = PurchaseLineSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = ("purchaseline",)
