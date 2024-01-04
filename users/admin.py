from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, ShippingAddress, PaymentInfo


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                    "name",
                    "avatar",
                    "gender",
                    "birthday",
                    "default_shipping_address",
                    "default_payment_info",
                    "agreed_to_terms_of_service",
                    "agreed_to_electronic_transactions",
                    "agreed_to_privacy_policy",
                    "confirmed_age_over_14",
                    "agreed_to_third_party_sharing",
                    "agreed_to_optional_privacy_policy",
                    "agreed_to_marketing_mails",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("last_login", "date_joined"),
                "classes": ("collapse",),
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "name",
    )


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "__str__",
    )


@admin.register(PaymentInfo)
class PaymentInfoAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "__str__",
    )
