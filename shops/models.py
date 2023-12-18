from django.db import models
import datetime
from common.models import CommonModel


# Create your models here.


class Shop(CommonModel):
    user = models.OneToOneField(
        "users.User", related_name="shop", on_delete=models.CASCADE
    )  # 한 유저 당 최대 한 개의 상점 개설 제한
    shop_name = models.CharField(max_length=256)
    avatar = models.URLField(blank=True, null=True)
    background_pic = models.URLField(blank=True, null=True)
    short_description = models.CharField(max_length=256, blank=True, null=True)
    announcement = models.CharField(max_length=256, blank=True, null=True)
    description_title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)

    subscription_expiration_date = models.DateField(blank=True, null=True)  # 구독 만료일
    auto_renewal_enabled = models.BooleanField(default=True)  # 자동 갱신 활성화 여부

    # SNS 연동 url
    instagram_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)

    is_star_seller = models.BooleanField(default=False)
    shop_policy_updated_at = models.DateField(
        blank=True, null=True, default=datetime.date.today
    )

    register_step = models.IntegerField(default=1)  # 상점 등록 절차 단계. step 4 까지
    is_activated = models.BooleanField(default=False)  # 운영 허가 완료

    def __str__(self):
        return self.shop_name


# TODO: shop, order 에 unique_together 옵션 추가할지? (이중 validation) / Common model을 상속받을 필요성
class Section(CommonModel):
    title = models.CharField(max_length=64)
    shop = models.ForeignKey(
        "Shop",
        on_delete=models.CASCADE,
        related_name="sections",
    )
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.title


# 상점 소개 이미지 TODO: 개수 제한 validation => 프론트로 충분한지?
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


# 상점 소개 영상. 최대 1개 제한
class ShopVideo(CommonModel):
    video = models.URLField()
    shop = models.OneToOneField(
        "Shop",
        on_delete=models.CASCADE,
        related_name="video",
    )

    def __str__(self):
        return f"{self.shop}"
