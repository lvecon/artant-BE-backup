from django.db import models
from common.models import CommonModel
from django.core.validators import MaxValueValidator


class Review(CommonModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    content = models.CharField(max_length=512)
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    rating_item_quality = models.PositiveIntegerField(
        validators=[MaxValueValidator(5)], null=True, blank=True
    )
    rating_shipping = models.PositiveIntegerField(
        validators=[MaxValueValidator(5)], null=True, blank=True
    )
    rating_customer_service = models.PositiveIntegerField(
        validators=[MaxValueValidator(5)], null=True, blank=True
    )

    def __str__(self):
        return f"{self.user} / {self.product}/ {self.content}"


class ReviewImage(CommonModel):
    image = models.URLField()
    review = models.ForeignKey(
        "Review",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="images",
    )

    def __str__(self):
        return f"{self.review} "


class ReviewResponse(CommonModel):
    review = models.OneToOneField(
        "Review",
        on_delete=models.CASCADE,
        related_name="reply",
    )
    shop = models.ForeignKey(
        "shops.Shop",
        on_delete=models.CASCADE,
        null=True,
        related_name="replies",
    )
    content = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.review} / {self.content}"
