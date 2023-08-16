from django.contrib import admin

from cart.models import Cart, CartLine


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "__iter__")


@admin.register(CartLine)
class CartAdmin(admin.ModelAdmin):
    list_display = ("variant",)
