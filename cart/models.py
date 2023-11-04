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

    def __iter__(self):
        return [str(cart_line) for cart_line in self.cartline.all()]


class CartLine(CommonModel):
    cart = models.ForeignKey(
        Cart,
        related_name="cartline",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        "products.Product",
        related_name="cartline",
        on_delete=models.CASCADE,
    )

    # variant = models.ManyToManyField(
    #     "products.VariantValue",
    #     related_name="+",
    #     blank=True,
    # )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} in {self.cart.user.name}"
