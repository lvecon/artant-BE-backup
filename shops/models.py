from django.db import models
import datetime
from common.models import CommonModel
from users.models import Address

# Create your models here.


class Shop(CommonModel):
    user = models.OneToOneField(
        "users.User", related_name="shop", on_delete=models.CASCADE
    )
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
        related_name="sections",
    )
    product = models.ManyToManyField(
        "products.Product",
        related_name="sections",
    )
