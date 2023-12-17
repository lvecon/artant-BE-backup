from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User


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
    shop_is_activated = serializers.SerializerMethodField()
    shop_register_step = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "pk",
            "shop_pk",
            "shop_name",
            "shop_avatar",
            "shop_is_activated",
            "shop_register_step",
            "username",
            "avatar",
            "email",
            "name",
            "gender",
            "birthday",
            "description",
            "birthday",
            "default_shipping_address",
            "default_payment_info",
        )

    def get_shop_pk(self, user):
        return user.shop.pk if hasattr(user, "shop") and user.shop else None

    def get_shop_name(self, user):
        return user.shop.shop_name if hasattr(user, "shop") and user.shop else None

    def get_shop_avatar(self, user):
        return user.shop.avatar if hasattr(user, "shop") and user.shop else None

    def get_shop_is_activated(self, user):
        return user.shop.is_activated if hasattr(user, "shop") and user.shop else None

    def get_shop_register_step(self, user):
        return user.shop.register_step if hasattr(user, "shop") and user.shop else None


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
        ]  # Include other relevant fields
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return value

    def validate_name(self, value):
        if User.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "A user with that nickname already exists."
            )
        return value

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
