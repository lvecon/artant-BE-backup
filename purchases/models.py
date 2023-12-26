from django.db import models
from django.core.validators import MinValueValidator

from common.models import CommonModel


class Purchase(CommonModel):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.user}'s purchase"


class PurchaseLine(CommonModel):
    purchase = models.ForeignKey(
        Purchase,
        related_name="purchase_lines",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        "products.Product",
        related_name="purchase_lines",
        on_delete=models.CASCADE,
    )

    # 기본 정보. TODO: 정책 기획 완료 시, 추가로 저장할 데이터 추가
    product_name = models.CharField(max_length=140)
    product_thumbnail = models.URLField()
    product_price = models.PositiveIntegerField()
    purchased_options = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} in {self.purchase}"
