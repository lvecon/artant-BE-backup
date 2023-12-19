from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Shop, Section
from users.serializers import TinyUserSerializer
from products.models import Product
from favorites.models import FavoriteShop


# index page shop banner 정보
class ShopBannerSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = (
            "pk",
            "background_pic",
        )


# index page 추천 판매자 정보
class FeaturedShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = (
            "pk",
            "avatar",
            "shop_name",
        )


# 당신이 좋아할 것 같은 상점
class RecommendedShopSerializer(ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = (
            "pk",
            "shop_name",
            "avatar",
            "thumbnails",
        )

    # 상점의 상품 썸네일 4개
    def get_thumbnails(self, shop):
        thumbnails = shop.products.all()[:4].values_list("thumbnail", flat=True)
        return list(thumbnails)


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
    images = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    common_sections = serializers.SerializerMethodField()
    featured_sections = serializers.SerializerMethodField()
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
            "common_sections",
            "featured_sections",
            "short_description",
            "description_title",
            "description",
            "subscription_expiration_date",
            "auto_renewal_enabled",
            "shop_policy_updated_at",
            "is_liked",
            "is_star_seller",
            "images",
            "video",
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

    def get_images(self, shop):
        images = shop.images.order_by("order").values("id", "image")
        return list(images)

    def get_video(self, shop):
        return shop.video.video if hasattr(shop, "video") and shop.video else None

    def get_common_sections(self, shop):
        common_sections = [{"title": "모든 작품", "product_count": shop.products.count()}]

        # "할인 중" 섹션 추가
        discount_products_count = sum(
            1 for product in shop.products.all() if (product.is_discount)
        )
        common_sections.append(
            {"title": "할인 중", "product_count": discount_products_count}
        )

        return common_sections

    def get_featured_sections(self, shop):
        featured_sections = []

        # 나머지 섹션들을 추가
        sections = Section.objects.filter(shop=shop).order_by("order")
        for section in sections:
            featured_sections.append(
                {
                    "id": section.pk,
                    "title": section.title,
                    "product_count": shop.products.filter(section=section).count(),
                }
            )

        return featured_sections


# 상점 등록. 처음 생성 시, 상점 이름만 입력
class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["shop_name", "user", "register_step"]
        extra_kwargs = {
            "user": {"read_only": True},
            "register_step": {"read_only": True},
            "shop_name": {"required": True},
        }

    def create(self, validated_data):
        # user와 register_step은 여기에서 추가로 설정
        validated_data["user"] = self.context["request"].user
        validated_data["register_step"] = 1
        return super().create(validated_data)


class ShopUpdateSerializer(serializers.ModelSerializer):
    sections_info = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

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
            "sections_info",
            "images",
            "video",
            "expiration",
            "cancellation",
            "shop_policy_updated_at",
            "instagram_url",
            "facebook_url",
            "website_url",
            "is_star_seller",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "id": {"read_only": True},
        }

    def get_sections_info(self, shop):
        sections = Section.objects.filter(shop=shop).order_by("order")
        return [
            {
                "id": section.pk,
                "title": section.title,
                "order": section.order,
                "product_count": shop.products.filter(section=section).count(),
            }
            for section in sections
        ]

    def get_images(self, shop):
        images = shop.images.order_by("order")
        return [
            {
                "id": image.pk,
                "image": image.image,
                "order": image.order,
            }
            for image in images
        ]

    def get_video(self, shop):
        return shop.video.video if hasattr(shop, "video") and shop.video else None


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "title", "order"]
