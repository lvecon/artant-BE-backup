from django.contrib import admin
from .models import Review, ReviewReply


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "content",
        "product",
    )
    list_filter = (
        # WordFilter,
        "rating",
    )


@admin.register(ReviewReply)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "review",
    )
