from django.db import models
from products.models import Product


# 최근 본 상품 기록
class UserProductTimestamp(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="+")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="+")
    timestamp = models.DateTimeField("Time Stamp", blank=True, null=True)
