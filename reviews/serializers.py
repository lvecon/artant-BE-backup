from rest_framework import serializers
from users.serializers import TinyUserSerializer
from products.serializers import TinyProductSerializer
from .models import Review, ReviewImage, ReviewResponse


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ("image",)


class ReviewResponseSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ReviewResponse
        fields = (
            "content",
            "created_at",
        )

    def get_created_at(self, obj):
        return obj.created_at.strftime("%m월%d일,%Y")


class ReviewSerializer(serializers.ModelSerializer):
    user = TinyUserSerializer(read_only=True)
    purchased_item = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    response = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "user",
            "purchased_item",
            "content",
            "rating",
            "rating_item_quality",
            "rating_shipping",
            "rating_customer_service",
            "created_at",
            "images",
            "response",
        )

    def get_purchased_item(self, review):
        product_name = review.purchase.product_name
        # 구매한 옵션 정보 가져오기 (옵션이 있는 경우)
        options = (
            f"{review.purchase.purchased_options}"
            if review.purchase.purchased_options
            else ""
        )

        return f"{product_name}({options})"

    def get_created_at(self, review):
        return review.created_at.strftime("%m월%d일,%Y")

    def get_images(self, review):
        images = review.images.all()
        image_urls = [image.image for image in images]

        return image_urls

    def get_response(self, review):
        if hasattr(review, "reply"):  # Check if reply exists
            return ReviewResponseSerializer(review.reply).data
        return None


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
