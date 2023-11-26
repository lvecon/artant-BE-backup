from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User
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

