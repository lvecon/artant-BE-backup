from django.contrib import admin

from products.models import (
    Product,
    ProductImage,
    ProductVideo,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "__str__",
        "price",
        "shop",
        "free_shipping",
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
