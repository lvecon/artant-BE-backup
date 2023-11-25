from django.db import models
from django.core.validators import MinValueValidator

from common.models import CommonModel


class Cart(CommonModel):
    user = models.OneToOneField(
        "users.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.user}'s cart"


class CartLine(CommonModel):
    cart = models.ForeignKey(
        Cart,
        related_name="cartlines",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cartlines",
    )
    product_variant = models.ForeignKey(
        "product_variants.ProductVariant",
        on_delete=models.CASCADE,
        related_name="cartlines",
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    personalization = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.product_variant} : {self.quantity} in {self.cart.user}'s cart"
