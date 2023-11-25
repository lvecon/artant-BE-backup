from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import Address, User


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("address_name", "street_address_1", "street_address_2")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "avatar",
                    "username",
                    "password",
                    "name",
                    "email",
                    "gender",
                    "birthday",
                    "description",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_confirmed",
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
