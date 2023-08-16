from django.contrib import admin

from updates.models import Update


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
