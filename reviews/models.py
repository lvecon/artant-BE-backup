from django.db import models

from common.models import CommonModel
from django.core.validators import MaxValueValidator


class Review(CommonModel):
    user = models.ForeignKey(
        "users.user",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    content = models.TextField()
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    raitng_item_quality = models.PositiveIntegerField(
        validators=[MaxValueValidator(5)], null=True, blank=True
    )
    raitng_shipping = models.PositiveIntegerField(
        validators=[MaxValueValidator(5)], null=True, blank=True
    )
    raitng_customer_service = models.PositiveIntegerField(
        validators=[MaxValueValidator(5)], null=True, blank=True
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    def __str__(self):
        return f"{self.user} / {self.product}/ {self.content}"


class ReviewPhoto(CommonModel):
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


class ReviewReply(CommonModel):
    review = models.OneToOneField(
        "Review",
        on_delete=models.CASCADE,
        related_name="reply",
    )
    shop = models.ForeignKey(
        "users.Shop",
        on_delete=models.CASCADE,
        null=True,
        related_name="reply",
    )
    content = models.TextField()

    def __str__(self):
        return f"{self.review} / {self.content}"
