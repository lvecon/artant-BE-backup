from django.db import models


# Create your models here.
class FavoriteProduct(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="favorites_products",
    )
    products = models.ManyToManyField(
        "products.Product",
        related_name="favorites_product",
    )

    def __str__(self):
        return f"{self.user}'s favorite products"


class FavoriteShop(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="favorites_shops",
    )
    shops = models.ManyToManyField(
        "shops.Shop",
        related_name="favorites_shop",
    )

    def __str__(self):
        return f"{self.user}'s favorite shops"
