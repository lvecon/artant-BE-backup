from django.contrib import admin

from order.models import Order, OrderLine


@admin.register(Order)
class OrdrerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "shop",
        "status",
        "created_at",
    )


@admin.register(OrderLine)
class OrdrerLineAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        # "variant",
        "quantity",
    )
