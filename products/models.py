from django.db import models

from common.models import CommonModel
from . import (
    ProductCreationDate,
    ProductMadeByChoices,
    ProductTypeChoices,
    ProductColorChoices,
    ProductItemTypeChoices,
)


class Category(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256, null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    background_image = models.ImageField(
        blank=True,
        null=True,
    )
    level = models.IntegerField()

    def __str__(self):
        return self.name

    def getDetail(self):
        return [detail.detail_name for detail in self.details.all()]


class CategoryDetail(models.Model):  # size, color, length
    category = models.ManyToManyField("Category", related_name="details")
    detail_name = models.CharField(max_length=32)

    def __str__(self):
        return self.detail_name

    def getCategory(self):
        return [category.name for category in self.category.all()]


class Color(models.Model):
    name = models.CharField(
        max_length=20,
        choices=ProductColorChoices.choices,
    )

    def __str__(self):
        return self.name


class DetailValue(models.Model):  # size-large, medium, small  color - red, green, blue
    detail_name = models.ForeignKey(
        "CategoryDetail",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
    )
    value = models.CharField(max_length=255)


class Product(CommonModel):
    """Model Definition for Products"""

    name = models.CharField(max_length=140)
    description = models.TextField()
    original_price = models.PositiveIntegerField(null=True, blank=True)
    price = models.PositiveIntegerField()
    shop = models.ForeignKey(
        "users.Shop",
        on_delete=models.CASCADE,
        related_name="product",
    )
    stock = models.PositiveIntegerField(null=True, blank=True)
    category = models.ManyToManyField(
        "Category",
        related_name="product",
    )
    made_by = models.CharField(
        max_length=140,
        choices=ProductMadeByChoices.choices,
    )
    product_type = models.CharField(
        max_length=140,
        choices=ProductTypeChoices.choices,
    )
    product_creation_date = models.CharField(
        max_length=140,
        choices=ProductCreationDate.choices,
    )
    product_item_type = models.CharField(
        max_length=140,
        choices=ProductItemTypeChoices.choices,
        default="Handmade",
    )
    colors = models.ManyToManyField(
        "products.Color",
        related_name="product",
    )
    processing_min = models.CharField(max_length=32, null=True, blank=True)
    processing_max = models.CharField(max_length=32, null=True, blank=True)
    shipping_price = models.CharField(max_length=32)
    item_weight = models.CharField(max_length=32, null=True, blank=True)
    item_weight_unit = models.CharField(max_length=32, null=True, blank=True)
    item_length = models.CharField(max_length=32, null=True, blank=True)
    item_width = models.CharField(max_length=32, null=True, blank=True)
    item_height = models.CharField(max_length=32, null=True, blank=True)

    has_variations = models.BooleanField(default=False)
    thumbnail = models.URLField()
    order_count = models.IntegerField(default=0)
    cart_count = models.IntegerField(default=0)
    is_best_seller = models.BooleanField(default=False)
    is_return_exchange_available = models.BooleanField(default=False)
    is_frame_included = models.BooleanField(default=False)
    is_giftcard_available = models.BooleanField(default=False)
    is_gift_wrapping_available = models.BooleanField(default=False)
    is_customizable = models.BooleanField(default=False)
    is_artant_star = models.BooleanField(default=False)
    is_artant_choice = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __iter__(self):
        return iter(self.tag)

    def rating(product):
        count = product.reviews.count()
        if count == 0:
            return 0
        else:
            total_rating = 0
            for review in product.reviews.all().values("rating"):
                total_rating += review["rating"]
            return round(total_rating / count, 2)

    def rating_count(product):
        return product.reviews.count()

    def free_shipping(product):
        return product.shipping_price == "0"

    def is_discount(product):
        return product.original_price > product.price

    def get_category(product):
        return product.category.get(level=2).name

    def get_shop_name(product):
        return product.shop.shop_name


class ProductTag(models.Model):
    tag = models.CharField(max_length=32)
    product = models.ManyToManyField(
        "Product",
        related_name="tag",
    )


class ProductImage(CommonModel):
    image = models.URLField()
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="images",
    )


class ProductVideo(CommonModel):
    video = models.URLField()
    product = models.OneToOneField(
        "Product",
        on_delete=models.CASCADE,
        related_name="video",
    )


class ProductVariant(CommonModel):
    name = models.CharField(max_length=255, blank=True)
    product = models.ForeignKey(
        "Product",
        related_name="variants",
        on_delete=models.CASCADE,
    )
    variant = models.ManyToManyField(
        "VariantValue",
        related_name="variant",
    )

    def __str__(self):
        return self.name

    def getVariant(self):
        return [vari.value for vari in self.variant.all()]


class VariantOption(models.Model):  # 개인맞춤화, 마감
    option = models.CharField(max_length=32)
    product = models.ForeignKey(
        "Product",
        related_name="options",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.option} for {self.product}"


class VariantValue(models.Model):  # 마감 - 거칠게, 부드럽게 등
    value = models.CharField(max_length=32)
    options = models.ForeignKey(
        "VariantOption",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.value


class UserProductTimestamp(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="timestamps"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="timestamps"
    )
    timestamp = models.DateTimeField("TTime Stamp", blank=True, null=True)
