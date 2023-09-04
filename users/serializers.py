from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Shop, User
from products.models import Product
from favorites.models import FavoriteShop


class TinyUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "pk",
            "name",
            "avatar",
            "username",
        )


class PrivateUserSerializer(ModelSerializer):
    shop_pks = serializers.SerializerMethodField()
    shop_names = serializers.SerializerMethodField()
    shop_avatars = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "pk",
            "shop_pks",
            "shop_names",
            "shop_avatars",
            "username",
            "avatar",
            "email",
            "name",
            "gender",
            "birthday",
            "description",
            "birthday",
            "default_shipping_address",
            "default_billing_address",
            "address",
        )

    def get_shop_pks(self, user):
        shop_pks = user.shop.values_list("pk", flat=True)
        return list(shop_pks)

    def get_shop_names(self, user):
        shop_pks = user.shop.values_list("shop_name", flat=True)
        return list(shop_pks)

    def get_shop_avatars(self, user):
        shop_pks = user.shop.values_list("avatar", flat=True)
        return list(shop_pks)


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

    users = TinyUserSerializer(many=True, read_only=True)

    class Meta:
        model = Shop
        fields = (
            "pk",
            "users",
            "shop_name",
            "avatar",
            "background_pic",
            "description",
            "announcement",
            "expiration",
            "cancellation",
            "shop_policy_updated_at",
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


class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"
