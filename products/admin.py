from django.contrib import admin

from products.models import (
    Category,
    CategoryDetail,
    DetailValue,
    Product,
    ProductImage,
    ProductTag,
    ProductVideo,
    UserProductTimestamp,
    Variation,
    VariationOption,
    ProductVariant,
    Color,
    Material,
)


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "parent",
        "getDetail",
    )
    list_filter = [
        "parent",
    ]


@admin.register(CategoryDetail)
class CategoryDetailAdmin(admin.ModelAdmin):
    list_display = ("detail_name", "getCategory")


@admin.register(Color)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name")


@admin.register(DetailValue)
class DetailValueAdmin(admin.ModelAdmin):
    list_display = (
        "detail_name",
        "product",
        "value",
    )


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("tag",)


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
    )


@admin.register(VariationOption)
class VariationOptionAdmin(admin.ModelAdmin):
    list_display = (
       "__str__",
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
       "id", "__str__",
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


@admin.register(UserProductTimestamp)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "timestamp",
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(ProductVideo)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("__str__",)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("__str__", )

