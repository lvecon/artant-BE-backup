from django.db import models
from django.core.validators import MinValueValidator

from common.models import CommonModel


class Cart(CommonModel):
    user = models.ForeignKey(
        "users.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
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

    def __str__(self):
        return f"{self.user}'s cart"

    def __iter__(self):
        return iter(self.lines.all())


class CartLine(CommonModel):
    cart = models.ForeignKey(
        Cart,
        related_name="lines",
        on_delete=models.CASCADE,
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        related_name="+",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
