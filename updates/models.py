from django.db import models

from common.models import CommonModel


class Update(CommonModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=256)
    contents = models.TextField()
    isReaded = models.BooleanField(default=False)
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
    )
    voucher = models.ForeignKey(
        "discount.Voucher",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.title} to {self.user}"
