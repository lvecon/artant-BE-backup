from django.contrib import admin

from events.models import event


@admin.register(event)
class ChattingRoomAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "contents",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at",)
