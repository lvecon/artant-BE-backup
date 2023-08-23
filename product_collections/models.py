from django.db import models

# Create your models here.
from django.db import models
from common.models import CommonModel


# Create your models here.
class Collection(CommonModel):
    title = models.CharField(max_length=256)
    contents = models.TextField()
    user = models.ManyToManyField(
        "users.User",
        related_name="collection",
    )
    product = models.ManyToManyField(
        "products.Product",
        related_name="collection",
    )

    def __str__(self):
        return self.title
