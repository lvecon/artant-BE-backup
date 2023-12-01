from django.contrib import admin
from .models import Shop, Section, ShopImage, ShopVideo

# Register your models here.


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shop_name",
        "description",
        "website_url",
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "shop",
        "title",
    )


@admin.register(ShopImage)
class ShopImageAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__",)


@admin.register(ShopVideo)
class ShopVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__",)
