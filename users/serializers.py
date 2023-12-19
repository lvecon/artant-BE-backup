from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User
from shops.models import Shop


class TinyUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "pk",
            "name",
            "avatar",
            "username",
        )


# PrivateUserSerializer에 사용
class MyShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = (
            "pk",
            "shop_name",
            "avatar",
            "is_activated",
            "register_step",
        )


class PrivateUserSerializer(ModelSerializer):
    shop = MyShopSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "pk",
            "name",
            "username",
            "email",
            "avatar",
            "gender",
            "birthday",
            "description",
            "shop",
            "default_shipping_address",
            "default_payment_info",
        )


class PublicUserSerializer(ModelSerializer):
    shop = MyShopSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "pk",
            "username",
            "email",
            "avatar",
            "description",
            "shop",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "name",
            "password",
            "email",
            "name",
            "gender",
            "birthday",
            "description",
            "username",
            "avatar",
        ]  # Include other relevant fieldsㅌㅈ
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            name=validated_data["name"],
            username=validated_data["username"],
            gender=validated_data["gender"],
            birthday=validated_data["birthday"],
            description=validated_data["description"],
            avatar=validated_data["avatar"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
