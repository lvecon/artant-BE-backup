from django.db import models
from common.models import CommonModel


# Create your models here.
class event(CommonModel):
    title = models.CharField(max_length=256)
    contents = models.TextField()
