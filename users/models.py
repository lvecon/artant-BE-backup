from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from common.models import CommonModel
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


class Shop(CommonModel):
    users = models.ManyToManyField("User", related_name="shop")
    avatar = models.URLField(blank=True, null=True)
    background_pic = models.URLField(blank=True, null=True)
    shop_name = models.CharField(max_length=256)
    description_title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    announcement = models.CharField(max_length=256, blank=True, null=True)
    expiration = models.TimeField(blank=True, null=True)
    address = models.OneToOneField(
        Address,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    cancellation = models.BooleanField(default=True)
    shop_policy_updated_at = models.DateField(
        blank=True, null=True, default=datetime.date.today
    )
    instagram_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    is_star_seller = models.BooleanField(default=False)
    image_1 = models.URLField(blank=True, null=True)
    image_2 = models.URLField(blank=True, null=True)
    image_3 = models.URLField(blank=True, null=True)
    image_4 = models.URLField(blank=True, null=True)
    image_5 = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.shop_name


class ShopTag(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    shop = models.ManyToManyField(
        Shop,
        blank=True,
        related_name="tags",
    )


class Section(models.Model):
    title = models.CharField(max_length=64)
    rank = models.PositiveIntegerField(null=True, unique=True)
    shop = models.ForeignKey(
        "Shop",
        on_delete=models.CASCADE,
        related_name="+",
    )
    product = models.ManyToManyField(
        "products.Product",
        related_name="+",
    )
