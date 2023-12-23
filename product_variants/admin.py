from django.contrib import admin
from .models import (
    Variation,
    VariationOption,
    ProductVariant,
)


# Register your models here.


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "__str__",
    )


@admin.register(VariationOption)
class VariationOptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "__str__",
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "__str__",
    )
