from django.db import models
from common.models import CommonModel
from django.core.validators import MinValueValidator

from . import OrderStatus


class Order(CommonModel):
    billing_address = models.ForeignKey(
        "users.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    shipping_address = models.ForeignKey(
        "users.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        "users.User",
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    shop = models.ForeignKey(
        "users.Shop",
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    status = models.CharField(
        max_length=32, default=OrderStatus.UNFULFILLED, choices=OrderStatus.CHOICES
    )


class OrderLine(CommonModel):
    order = models.ForeignKey(
        Order,
        related_name="lines",
        editable=False,
        on_delete=models.CASCADE,
    )
    # variant = models.ForeignKey(
    #     # "products.VariantValue",
    #     related_name="order_lines",
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    # )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
