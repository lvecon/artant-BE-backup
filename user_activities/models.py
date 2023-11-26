from django.db import models
from products.models import Product

# Create your models here.
class UserProductTimestamp(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="+"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="+"
    )
    timestamp = models.DateTimeField("Time Stamp", blank=True, null=True)