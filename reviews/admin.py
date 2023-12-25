from django.contrib import admin
from .models import Review, ReviewResponse, ReviewImage


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "content",
        "product",
    )
    list_filter = ("rating",)


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
