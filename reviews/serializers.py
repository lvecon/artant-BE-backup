from rest_framework import serializers
from users.serializers import TinyUserSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = TinyUserSerializer(read_only=True)  # read only. valid even no User

    product_thumbnail = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "user",
            "content",
            "rating",
            "created_at",
            "raitng_item_quality",
            "raitng_shipping",
            "raitng_customer_service",
            "product_name",
            "product_thumbnail",
        )

    def get_product_thumbnail(self, review):
        return review.product.thumbnail

    def get_product_name(self, review):
        return review.product.name
