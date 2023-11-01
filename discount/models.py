from datetime import timezone
from django.db import models
from . import DiscountType, DiscountValueType, VoucherType


class voucher(models.Model):
    class DiscountValueType:
        FIXED = "fixed"
        PERCENTAGE = "percentage"

        CHOICES = [
            (FIXED, "fixed"),
            (PERCENTAGE, "%"),
        ]

    type = models.CharField(
        max_length=20,
        choices=VoucherType.CHOICES,
        default=VoucherType.ENTIRE_ORDER,
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True, db_index=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    discount_value_type = models.CharField(
        max_length=10,
        choices=DiscountValueType.CHOICES,
        default=DiscountValueType.FIXED,
    )
    discount_value = models.CharField(
        max_length=10,
    )
    # not mandatory fields, usage depends on type
    products = models.ManyToManyField(
        "products.Product", blank=True, related_name="voucher"
    )
    # variants = models.ManyToManyField("products.VariantValue", blank=True)
    categories = models.ManyToManyField("products.Category", blank=True)


class Sale(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=10,
        choices=DiscountValueType.CHOICES,
        default=DiscountValueType.FIXED,
    )
    categories = models.ManyToManyField("products.Category", blank=True)
    products = models.ManyToManyField("products.Product", blank=True)
    # variants = models.ManyToManyField("products.VariantValue", blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    discount_value = models.CharField(
        max_length=10,
    )
