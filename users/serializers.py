from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User
from shops.models import Shop
import re
from .utils import check_phone_number


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


class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "name",
            "username",
            "gender",
            "birthday",
            "cell_phone_number",
            "description",
            "avatar",
            "is_corporate",
            "corporate_number",
            "corporate_name",
            "agreed_to_terms_of_service",
            "agreed_to_electronic_transactions",
            "agreed_to_privacy_policy",
            "confirmed_age_over_14",
            "agreed_to_third_party_sharing",
            "agreed_to_optional_privacy_policy",  # 선택적 동의 필드 추가
            "agreed_to_marketing_mails",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        # 비밀번호 일치 확인
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords must match.")

        # 필수 약관 동의 확인
        if (
            not data.get("agreed_to_terms_of_service")
            or not data.get("agreed_to_electronic_transactions")
            or not data.get("agreed_to_privacy_policy")
            or not data.get("confirmed_age_over_14")
            or not data.get("agreed_to_third_party_sharing")
        ):
            raise serializers.ValidationError("모든 필수 약관에 동의해야 합니다.")

        # 일반 법인 여부 확인
        if data.get("is_corporate"):
            if not data.get("corporate_number"):
                raise serializers.ValidationError(
                    "Corporate number is required for corporate users."
                )
            if not data.get("corporate_name"):
                raise serializers.ValidationError(
                    "Corporate name is required for corporate users."
                )
        return data

    def validate_cell_phone_number(self, value):
        result = check_phone_number(value)
        if "error" in result:
            raise ValidationError(result["error"])
        return value

    # TODO: 필요시 비밀번호 유효성 검사 로직 보안.
    def validate_password(self, value):
        # 영문, 숫자, 특수문자 포함 여부 확인
        if not re.findall("[A-Za-z]", value):
            raise serializers.ValidationError("비밀번호에는 최소 한 개의 영문자가 포함되어야 합니다.")
        if not re.findall("[0-9]", value):
            raise serializers.ValidationError("비밀번호에는 최소 한 개의 숫자가 포함되어야 합니다.")
        if not re.findall('[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("비밀번호에는 최소 한 개의 특수 문자가 포함되어야 합니다.")

        # 같은 문자가 3개 이상 연속되지 않도록 확인
        for i in range(len(value) - 2):
            if value[i] == value[i + 1] == value[i + 2]:
                raise serializers.ValidationError("비밀번호에 같은 문자가 3번 연속으로 사용될 수 없습니다.")

        return value

    def create(self, validated_data):
        user_data = {
            k: v
            for k, v in validated_data.items()
            if k != "password" and k != "password_confirm"
        }
        user = User.objects.create(**user_data)
        user.set_password(validated_data["password"])
        user.save()
        return user
