from django.db import models

from . import (
    ProductColorChoices,
)


class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )  # 상위 카테고리 ex) 회화 -> 유화, 수채화
    level = models.PositiveIntegerField()  # Art & Collections = 1, 회화 = 2, 수채화 = 3
    description = models.CharField(max_length=256, null=True, blank=True)
    background_image = models.URLField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(
        max_length=20, choices=ProductColorChoices.choices, unique=True
    )

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name
