from django.db import models
from common.models import CommonModel


# Create your models here.
class Event(CommonModel):
    title = models.CharField(max_length=256)
    contents = models.TextField()

    def __str__(self):
        return self.title


class EventImage(CommonModel):
    image = models.URLField()
    event = models.ForeignKey(
        "Event",
        on_delete=models.CASCADE,
        related_name="image",
    )

    def __str__(self):
        return f"{self.event}"
