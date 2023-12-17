from django.db import models
import datetime
from common.models import CommonModel


# Create your models here.


class Shop(CommonModel):
    user = models.OneToOneField(
        "users.User", related_name="shop", on_delete=models.CASCADE
    )
    is_activated = models.BooleanField(default=False)
    register_step = models.IntegerField(default=1)
    avatar = models.URLField(blank=True, null=True)
    background_pic = models.URLField(blank=True, null=True)
    shop_name = models.CharField(max_length=256)
    short_description = models.CharField(max_length=256, default="")
    description_title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    announcement = models.CharField(max_length=256, blank=True, null=True)
    expiration = models.DateField(blank=True, null=True)
    cancellation = models.BooleanField(default=True)
    shop_policy_updated_at = models.DateField(
        blank=True, null=True, default=datetime.date.today
    )
    instagram_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    is_star_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.shop_name


# TODO: shop, order 에 unique_together 옵션 추가할지 의논 / Common model을 쓸 필요성
class Section(CommonModel):
    title = models.CharField(max_length=64)
    shop = models.ForeignKey(
        "Shop",
        on_delete=models.CASCADE,
        related_name="sections",
    )
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class ShopImage(CommonModel):
    image = models.URLField()
    shop = models.ForeignKey(
        "Shop",
        on_delete=models.CASCADE,
        related_name="images",
    )
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.shop}"


class ShopVideo(CommonModel):
    video = models.URLField()
    shop = models.OneToOneField(
        "Shop",
        on_delete=models.CASCADE,
        related_name="video",
    )

    def __str__(self):
        return f"{self.shop}"
