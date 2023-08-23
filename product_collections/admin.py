from django.contrib import admin

from .models import Collection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_at",
    )
    list_filter = ("created_at",)
