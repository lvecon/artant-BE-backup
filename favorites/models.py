from django.db import models


# Create your models here.
class FavoriteProduct(models.Model):
    products = models.ManyToManyField(
        "products.Product",
        related_name="favorites_item",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="favorites_items",
    )

    def __str__(self):
        return f"{self.user}'s favorite items"


class FavoriteShop(models.Model):
    shops = models.ManyToManyField(
        "shops.Shop",
        related_name="favorites_shop",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="favorites_shops",
    )

    def __str__(self):
        return f"{self.user}'s favorite shops"
