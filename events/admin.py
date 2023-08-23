from django.contrib import admin

from events.models import Event, EventImage


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "contents",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at",)


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
