from django.contrib import admin
from user_activities.models import UserProductTimestamp

# Register your models here.
@admin.register(UserProductTimestamp)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "timestamp",
    )
