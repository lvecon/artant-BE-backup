from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from favorites.models import FavoriteItem
from .models import (
    Product,
    ProductImage,
    ProductTag,
    ProductVideo,
    Color,
    VariantOption,
    VariantValue,
)
from datetime import datetime, timedelta
from users.serializers import TinyUserSerializer


class ProductTagSerializer(ModelSerializer):
    class Meta:
        model = ProductTag
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("pk", "image")


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ("pk", "video")


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ("pk", "name")


class VariantValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantValue
        fields = ("value",)


class VariantOptionSerializer(serializers.ModelSerializer):
    value = VariantValueSerializer(many=True, read_only=True)

    class Meta:
        model = VariantOption
        fields = ["name", "value"]


class ProductDetailSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_star_seller = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    shop_pk = serializers.SerializerMethodField()
    discount_rate = serializers.SerializerMethodField()
    sellers = serializers.SerializerMethodField()
    shipping_date = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)
    colors = ColorSerializer(many=True, read_only=True)
    video = VideoSerializer()
    options = VariantOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "shop_pk",
            "shop_name",
            "sellers",
            "original_price",
            "price",
            "discount_rate",
            "rating",
            "rating_count",
            "stock",
            "cart_count",
            "shipping_price",
            "free_shipping",
            "processing_min",
            "processing_max",
            "shipping_date",
            "is_return_exchange_available",
            "is_frame_included",
            "is_artant_choice",
            "is_artant_star",
            "colors",
            "product_item_type",
            "is_giftcard_available",
            "is_gift_wrapping_available",
            "is_customizable",
            "images",
            "video",
            "is_best_seller",
            "is_star_seller",
            "is_liked",
            "thumbnail",
            "created_at",
            "category",
            "options",
            "item_width",
            "item_height",
            "description",
        )

    def get_rating(self, product):
        return product.rating()

    def get_is_liked(self, product):
        request = self.context.get("request")
        if request:
            if request.user.is_authenticated:
                return FavoriteItem.objects.filter(
                    user=request.user,
                    products__pk=product.pk,
                ).exists()
        return False

    def get_category(self, product):
        return product.category.get(level=2).name

    def get_shop_name(self, product):
        return product.shop.shop_name

    def get_shop_pk(self, product):
        return product.shop.pk

    def get_sellers(self, product):
        users = product.shop.users.all()
        serializer = TinyUserSerializer(users, many=True)
        return serializer.data

    def get_is_star_seller(self, product):
        return product.shop.is_star_seller

    def get_discount_rate(self, product):
        if product.original_price & product.price:
            return int((1 - product.price / product.original_price) * 100)
        else:
            return 0

    def get_shipping_date(self, product):
        today = datetime.now().date()  # 현재 날짜
        processing_min = int(product.processing_min)  # 최소 처리 기간
        processing_max = int(product.processing_max)  # 최대 처리 기간

        min_shipping_date = today + timedelta(days=processing_min)
        max_shipping_date = today + timedelta(days=processing_max)

        return f"{min_shipping_date.month}월 {min_shipping_date.day}일 ~ {max_shipping_date.month}월 {max_shipping_date.day}일"


class ProductListSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    discount_rate = serializers.SerializerMethodField()
    is_star_seller = serializers.SerializerMethodField()
    # colors = ColorSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "shop_name",
            "original_price",
            "price",
            "discount_rate",
            "rating",
            "rating_count",
            "free_shipping",
            "is_discount",
            # "is_frame_included",
            # "is_artant_choice",
            # "is_artant_star",
            # "colors",
            # "product_item_type",
            # "is_giftcard_available",
            # "is_gift_wrapping_available",
            # "is_customizable",
            "is_best_seller",
            "is_star_seller",
            "is_liked",
            "thumbnail",
            # "created_at",
            # "category",
        )

    def get_rating(self, product):
        return product.rating()

    def get_is_liked(self, product):
        request = self.context.get("request")

        if request:
            if request.user.is_authenticated:
                return FavoriteItem.objects.filter(
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


class TinyProductSerializer(serializers.ModelSerializer):
    discount_rate = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "original_price",
            "price",
            "discount_rate",
        )

    def get_discount_rate(self, product):
        if product.original_price & product.price:
            return int((1 - product.price / product.original_price) * 100)
        else:
            return 0
