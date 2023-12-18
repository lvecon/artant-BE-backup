from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from common.models import CommonModel
from . import (
    ProductCreationDate,
    ProductMadeByChoices,
    ProductTypeChoices,
    ProductItemTypeChoices,
)

from product_attributes.models import Color


# TODO: 리뷰 수, 별점 관리 방법. 필드? 함수? / 할인가 관리방법 미정
class Product(CommonModel):
    shop = models.ForeignKey(
        "shops.Shop",
        on_delete=models.CASCADE,
        related_name="products",
    )
    name = models.CharField(max_length=140)
    description = models.TextField()

    price = models.PositiveIntegerField()
    original_price = models.PositiveIntegerField(null=True, blank=True)
    is_discount = models.BooleanField(default=False)

    quantity = models.PositiveIntegerField(null=True, blank=True, default=1)
    sku = models.CharField(max_length=140, null=True, blank=True)
    category = models.ManyToManyField(
        "product_attributes.Category",
        related_name="product",
    )
    tags = models.ManyToManyField(
        "product_attributes.ProductTag",
        related_name="products",
        null=True,
        blank=True,
    )
    made_by = models.CharField(
        max_length=140,
        choices=ProductMadeByChoices.choices,
        default="I did",
    )
    product_type = models.CharField(
        max_length=140,
        choices=ProductTypeChoices.choices,
        default="A finished product",
    )
    product_creation_date = models.CharField(
        max_length=140,
        choices=ProductCreationDate.choices,
        default="Made To Order",
    )
    product_item_type = models.CharField(
        max_length=140,
        choices=ProductItemTypeChoices.choices,
        default="Handmade",
    )
    primary_color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_color_products",
    )
    secondary_color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secondary_color_products",
    )
    materials = models.ManyToManyField("product_attributes.Material", blank=True)
    section = models.ForeignKey(
        "shops.Section",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="section",
    )

    processing_min = models.CharField(max_length=32, default=3)
    processing_max = models.CharField(max_length=32, default=7)
    shipping_price = models.CharField(max_length=32, default=0)
    item_weight = models.CharField(max_length=32, null=True, blank=True)
    item_weight_unit = models.CharField(max_length=32, null=True, blank=True)
    item_length = models.CharField(max_length=32, null=True, blank=True, default=20)
    item_width = models.CharField(max_length=32, null=True, blank=True, default=60)
    item_height = models.CharField(max_length=32, null=True, blank=True, default=90)

    has_variations = models.BooleanField(default=False)
    thumbnail = models.URLField()
    order_count = models.IntegerField(blank=True, default=0)

    is_best_seller = models.BooleanField(default=False)
    is_return_exchange_available = models.BooleanField(default=False)
    is_frame_included = models.BooleanField(default=False)
    is_giftcard_available = models.BooleanField(default=False)
    is_gift_wrapping_available = models.BooleanField(default=False)
    is_customizable = models.BooleanField(default=False)
    is_artant_star = models.BooleanField(default=False)
    is_artant_choice = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)

    is_personalization_enabled = models.BooleanField(default=False)
    is_personalization_optional = models.BooleanField(default=False)
    personalization_guide = models.CharField(max_length=32, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def __iter__(self):
        return iter(self.tag)

    def save(self, *args, **kwargs):
        # 할인 여부를 설정
        if self.original_price and self.price < self.original_price:
            self.is_discounted = True
        else:
            self.is_discounted = False

        super().save(*args, **kwargs)


# TODO: 할인 적용 방식 기획 나오면 수정
@receiver(pre_save, sender=Product)
def set_original_price(sender, instance, **kwargs):
    if instance.original_price is None or instance.price > instance.original_price:
        instance.original_price = instance.price


class ProductImage(CommonModel):
    image = models.URLField()
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="images",
    )
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product}"


class ProductVideo(CommonModel):
    video = models.URLField()
    product = models.OneToOneField(
        "Product",
        on_delete=models.CASCADE,
        related_name="video",
    )

    def __str__(self):
        return f"{self.product}"
