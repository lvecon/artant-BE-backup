from rest_framework import serializers
from users.serializers import TinyUserSerializer
from products.serializers import TinyProductSerializer
from .models import Review, ReviewPhoto, ReviewReply
from datetime import datetime


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewPhoto
        fields = ("pk", "image")


class ReviewReplySerializer(serializers.ModelSerializer):
    shop_pk = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ReviewReply
        fields = (
            "shop_pk",
            "shop_name",
            "content",
            "created_at",
        )

    def get_shop_pk(self, reply):
        return reply.shop.pk

    def get_shop_name(self, reply):
        return reply.shop.shop_name

    def get_created_at(self, review):
        return review.created_at.strftime("%Y-%m-%d")


class ReviewSerializer(serializers.ModelSerializer):
    user = TinyUserSerializer(read_only=True)  # read only. valid even no User
    images = ReviewImageSerializer(many=True, read_only=True)
    reply = ReviewReplySerializer()
    product_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "pk",
            "user",
            "product_name",
            "content",
            "rating",
            "created_at",
            "raitng_item_quality",
            "raitng_shipping",
            "raitng_customer_service",
            "images",
            "reply",
        )

    def get_product_name(self, review):
        return review.product.name

    def get_created_at(self, review):
        return review.created_at.strftime("%Y-%m-%d")


class ReviewDetailSerializer(serializers.ModelSerializer):
    user = TinyUserSerializer(read_only=True)  # read only. valid even no User
    product = TinyProductSerializer()

    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "user",
            "product",
            "content",
            "rating",
            "created_at",
        )

    def get_created_at(self, review):
        return review.created_at.strftime("%Y-%m-%d")
