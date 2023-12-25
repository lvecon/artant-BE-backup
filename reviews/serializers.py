from rest_framework import serializers
from users.serializers import TinyUserSerializer
from products.serializers import TinyProductSerializer
from .models import Review, ReviewImage, ReviewResponse


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ("pk", "image")


class ReviewResponseSerializer(serializers.ModelSerializer):
    shop_pk = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ReviewResponse
        fields = (
            "pk",
            "shop_pk",
            "shop_name",
            "avatar",
            "content",
            "created_at",
        )

    def get_shop_pk(self, reply):
        return reply.shop.pk

    def get_shop_name(self, reply):
        return reply.shop.shop_name

    def get_avatar(self, reply):
        return reply.shop.avatar

    def get_created_at(self, review):
        return review.created_at.strftime("%Y-%m-%d")


class ReviewSerializer(serializers.ModelSerializer):
    user = TinyUserSerializer(read_only=True)  # read only. valid even no User
    images = ReviewImageSerializer(many=True, read_only=True)
    reply = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_thumbnail = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "pk",
            "user",
            "product_name",
            "content",
            "product_thumbnail",
            "rating",
            "created_at",
            "rating_item_quality",
            "rating_shipping",
            "rating_customer_service",
            "images",
            "reply",
        )

    def get_product_name(self, review):
        return review.product.name

    def get_product_thumbnail(self, review):
        return review.product.thumbnail

    def get_created_at(self, review):
        return review.created_at.strftime("%Y-%m-%d")

    def get_reply(self, obj):
        if hasattr(obj, "reply"):  # Check if reply exists
            return ReviewResponseSerializer(obj.reply).data
        return None  # No reply, return None or any suitable value


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
