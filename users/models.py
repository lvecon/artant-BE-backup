from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from users import UserGenderChoices


# TODO: 개인정보 페이지 기획 완료 시 수정
class User(AbstractUser):
    name = models.CharField(max_length=256, unique=True)
    email = models.EmailField(unique=True)
    avatar = models.URLField(blank=True, null=True)
    gender = models.CharField(
        max_length=16, choices=UserGenderChoices.choices, null=True, default="Female"
    )
    birthday = models.DateField(null=True, default=datetime.date(1977, 7, 7))
    is_confirmed = models.BooleanField(default=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    default_shipping_address = models.OneToOneField(
        "Address",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    default_billing_address = models.OneToOneField(
        "Address",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name


class Address(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="addresses"
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
