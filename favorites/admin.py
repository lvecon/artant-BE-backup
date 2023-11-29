from django.contrib import admin

from favorites.models import FavoriteShop, FavoriteProduct


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(FavoriteShop)
class FavoriteShopAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
