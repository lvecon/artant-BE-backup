from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Shop, Section
from users.serializers import TinyUserSerializer
from products.models import Product
from favorites.models import FavoriteShop


class TinyShopSerializer(ModelSerializer):
    # 추가: 4개까지의 썸네일을 가져올 필드 정의
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = (
            "pk",
            "shop_name",
            "avatar",
            "background_pic",
            "is_star_seller",
            "thumbnails",  # thumbnails 필드 추가
        )

    # 추가: 썸네일 정보 가져오는 메서드 정의
    def get_thumbnails(self, obj):
        # 샵에 해당하는 최대 4개의 상품 썸네일을 가져옵니다.
        products = Product.objects.filter(shop=obj)[:4]
        thumbnail_list = []

        for product in products:
            if product.thumbnail:
                thumbnail_list.append(product.thumbnail)

        return thumbnail_list


class ShopSerializer(ModelSerializer):
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = (
            "pk",
            "shop_name",
            "avatar",
            "background_pic",
            "is_liked",
            "is_star_seller",
        )

    def get_is_liked(self, shop):
        request = self.context.get("request")
        if request:
            if request.user.is_authenticated:
                return FavoriteShop.objects.filter(
                    user=request.user,
                    shops__pk=shop.pk,
                ).exists()
        return False


class ShopDetailSerializer(ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    sections_info = serializers.SerializerMethodField()
    user = TinyUserSerializer(read_only=True)

    class Meta:
        model = Shop
        fields = (
            "pk",
            "user",
            "shop_name",
            "avatar",
            "background_pic",
            "announcement",
            "sections_info",
            "short_description",
            "description_title",
            "description",
            "expiration",
            "cancellation",
            "shop_policy_updated_at",
            "is_liked",
            "is_star_seller",
            "image_urls",
        )

    def get_is_liked(self, shop):
        request = self.context.get("request")
        if request:
            if request.user.is_authenticated:
                return FavoriteShop.objects.filter(
                    user=request.user,
                    shops__pk=shop.pk,
                ).exists()
        return False

    def get_image_urls(self, shop):
        image_fields = ["image_1", "image_2", "image_3", "image_4", "image_5"]
        image_urls = [
            getattr(shop, field) for field in image_fields if getattr(shop, field)
        ]
        return image_urls

    def get_sections_info(self, shop):
        sections = Section.objects.filter(shop=shop)
        return [
            {
                "title": section.title,
                "product_count": shop.products.filter(section=section).count(),
            }
            for section in sections
        ]


class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"


class ShopUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            "is_activated",
            "register_step",
            "avatar",
            "background_pic",
            "shop_name",
            "short_description",
            "description_title",
            "description",
            "announcement",
            "expiration",
            "address",
            "cancellation",
            "shop_policy_updated_at",
            "instagram_url",
            "facebook_url",
            "website_url",
            "is_star_seller",
            "image_1",
            "image_2",
            "image_3",
            "image_4",
            "image_5",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "id": {"read_only": True},
        }

    def update(self, instance, validated_data):
        # Update the Shop instance with the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "title", "rank", "shop"]
