from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

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
        "shops.Shop",
        on_delete=models.CASCADE,
        related_name="product",
    )
    quantity = models.PositiveIntegerField(null=True, blank=True, default=1)
    sku = models.CharField(max_length=140, null=True, blank=True)
    category = models.ManyToManyField(
        "Category",
        related_name="product",
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
    primary_color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_color_products')
    secondary_color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name='secondary_color_products')
    materials = models.ManyToManyField('Material', blank=True)

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


@receiver(pre_save, sender=Product)
def set_original_price(sender, instance, **kwargs):
    if instance.original_price is None:
        instance.original_price = instance.price


class ProductTag(models.Model):
    tag = models.CharField(max_length=32, unique=True)
    product = models.ManyToManyField(
        "Product",
        related_name="tags",
    )


class ProductImage(CommonModel):
    image = models.URLField()
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="images",
    )

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


class Variation(models.Model):
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    is_sku_vary = models.BooleanField(default=False) 
    is_price_vary = models.BooleanField(default=False) 
    is_quantity_vary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} : {self.product.name}"

class VariationOption(models.Model):
    name = models.CharField(max_length=255, null=True)
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, null=True, related_name='options')

    def __str__(self):
        return f"{self.variation.name} - {self.name} : {self.variation.product.name}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    option_one = models.ForeignKey(VariationOption, on_delete=models.CASCADE, related_name='variants_as_option_one', null=True, blank=True)
    option_two = models.ForeignKey(VariationOption, on_delete=models.CASCADE, related_name='variants_as_option_two', null=True, blank=True)
    sku = models.CharField(max_length=255, null=True, blank=True)
    price = models.PositiveIntegerField(null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        options = filter(None, [self.option_one, self.option_two])
        option_descriptions = " x ".join(option.name for option in options)
        return f"{self.product.name} - {option_descriptions}"

class UserProductTimestamp(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="timestamps"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="timestamps"
    )
    timestamp = models.DateTimeField("TTime Stamp", blank=True, null=True)



class Material(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name}"
