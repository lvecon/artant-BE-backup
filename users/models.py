from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from users import UserGenderChoices


# TODO: 개인정보 페이지 기획 완료 시 수정
class User(AbstractUser):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    avatar = models.URLField(blank=True, null=True)
    gender = models.CharField(max_length=16, choices=UserGenderChoices.choices)
    birthday = models.DateField(blank=True, null=True)
    cell_phone_number = models.CharField(max_length=11)
    description = models.CharField(max_length=256, blank=True, null=True)
    default_shipping_address = models.OneToOneField(
        "ShippingAddress",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    default_payment_info = models.OneToOneField(
        "PaymentInfo",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # 필수 약관 동의
    agreed_to_terms_of_service = models.BooleanField(default=False)  # 아트앤트 이용약관
    agreed_to_electronic_transactions = models.BooleanField(
        default=False
    )  # 전자금융거래 이용약관
    agreed_to_privacy_policy = models.BooleanField(default=False)  # 개인정보 수집 및 이용
    confirmed_age_over_14 = models.BooleanField(default=False)  # 만 14세 이상
    agreed_to_third_party_sharing = models.BooleanField(default=False)  # 개인정보 제3자 제공

    # 선택 약관 동의
    agreed_to_optional_privacy_policy = models.BooleanField(
        default=False
    )  # 선택 개인정보 수집 동의
    agreed_to_marketing_mails = models.BooleanField(default=False)  # 광고성 정보 수신 동의

    def __str__(self):
        return self.name


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="shipping_addresses"
    )
    recipient_name = models.CharField(max_length=100)  # 받는 사람
    street_name_address = models.CharField(max_length=100)  # 도로명 주소
    street_number_address = models.CharField(max_length=100)  # 지번 주소
    postal_code = models.CharField(max_length=5)  # 우편 번호
    detail_address = models.CharField(max_length=100)  # 상세주소
    cell_phone_number = models.CharField(max_length=11)  # 휴대폰 번호
    delivery_instructions = models.TextField(
        blank=True, null=True
    )  # 배송 요청사항 TODO: choice 생성 (문 앞, 경비실 .. / 공동 현관 출입번호)

    def __str__(self):
        return f"{self.street_name_address}, {self.postal_code}"


class PaymentInfo(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)

    def __str__(self):
        return f"**** **** **** {self.card_number[-4:]}"
