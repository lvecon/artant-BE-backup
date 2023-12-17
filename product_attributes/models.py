from django.db import models

from . import (
    ProductColorChoices,
)


class Category(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256, null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    background_image = models.ImageField(
        blank=True,
        null=True,
    )
    level = models.IntegerField()

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(
        max_length=20,
        choices=ProductColorChoices.choices,
    )

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    tag = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f"{self.tag}"


class Material(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name}"
