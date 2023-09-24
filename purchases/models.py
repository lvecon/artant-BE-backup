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

    def __iter__(self):
        return [str(purchase_line) for purchase_line in self.purchaseline.all()]


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

    variant = models.ManyToManyField(
        "products.VariantValue",
        related_name="+",
        blank=True,
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    order_date = models.CharField(
        null=True, blank=True, max_length=20
    )  # 주문한 날짜를 문자열로 저장

    def __str__(self):
        return f"{self.product.name} in {self.purchase.user.name}"
