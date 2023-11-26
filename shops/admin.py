from django.contrib import admin
from .models import Shop, Section

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
