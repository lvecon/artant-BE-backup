from django.db import models

from common.models import CommonModel


class Payment(CommonModel):
    order = models.ForeignKey(
        "order.Order",
        on_delete=models.CASCADE,
    )
    address = models.ForeignKey(
        "users.Address",
        on_delete=models.CASCADE,
    )
    currency = models.CharField(max_length=32, default="KR Won")
