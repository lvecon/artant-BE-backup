from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from users import UserGenderChoices


class Address(models.Model):
    user_name = models.CharField(max_length=256)
    address_name = models.CharField(max_length=256, blank=True, null=True)
    cell_phone_number = models.CharField(max_length=16)  # 휴대전화 번호
    phone_number = models.CharField(max_length=16, blank=True, null=True)  # 전화번호
    postal_code = models.CharField(max_length=6)
    street_address_1 = models.CharField(max_length=256)
    street_address_2 = models.CharField(max_length=256)
    note = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.address_name


class User(AbstractUser):
    avatar = models.URLField(
        blank=True,
        null=True,
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=256, unique=True)
    gender = models.CharField(
        max_length=16, choices=UserGenderChoices.choices, null=True, default="Female"
    )
    birthday = models.DateField(null=True, default=datetime.date(1977, 7, 7))
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_confirmed = models.BooleanField(default=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    address = models.ManyToManyField(
        Address,
        blank=True,
        related_name="+",
    )
    default_shipping_address = models.OneToOneField(
        Address,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    default_billing_address = models.OneToOneField(
        Address,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name

