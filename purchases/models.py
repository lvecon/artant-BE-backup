from django.db import models
from django.core.validators import MinValueValidator

from common.models import CommonModel


class Purchase(CommonModel):
    user = models.OneToOneField(
        "users.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.user}'s purchase"


class PurchaseLine(CommonModel):
    purchase = models.ForeignKey(
        Purchase,
        related_name="purchaseline",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        "products.Product",
        related_name="purchaseline",
        on_delete=models.CASCADE,
    )
    purchased_options = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} in {self.purchase}"
