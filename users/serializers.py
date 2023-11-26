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
    shop_pk = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    shop_avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "pk",
            "shop_pk",
            "shop_name",
            "shop_avatar",
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

    def get_shop_pk(self, user):
        return user.shop.pk if user.shop else None

    def get_shop_name(self, user):
        return user.shop.shop_name if user.shop else None

    def get_shop_avatar(self, user):
        return user.shop.avatar if user.shop else None
