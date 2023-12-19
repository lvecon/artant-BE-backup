from django.contrib import admin

from .models import (
    Category,
    ProductTag,
    Color,
    Material,
)


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "parent",
    )
    list_filter = [
        "parent",
    ]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
