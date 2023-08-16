from django.contrib import admin

from discount.models import Sale, voucher


@admin.register(voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "discount_value_type",
    )


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
    )
