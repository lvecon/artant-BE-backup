from django.contrib import admin

from favorites.models import FavoriteShop, FavoritesItem


@admin.register(FavoritesItem)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(FavoriteShop)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
