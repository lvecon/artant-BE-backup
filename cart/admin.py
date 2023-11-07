from django.contrib import admin

from cart.models import Cart, CartLine


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
      list_display = (
        "__str__",
    )



@admin.register(CartLine)
class CartLineAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
    )
