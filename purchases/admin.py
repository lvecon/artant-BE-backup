from django.contrib import admin

from purchases.models import Purchase, PurchaseLine


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "__iter__")


@admin.register(PurchaseLine)
class PurchaseLineAdmin(admin.ModelAdmin):
    list_display = (
        "purchase",
        "product",
    )
