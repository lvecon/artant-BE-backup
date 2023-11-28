from django.contrib import admin

from favorites.models import FavoriteShop, FavoriteItem


@admin.register(FavoriteItem)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(FavoriteShop)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
