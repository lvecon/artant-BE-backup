from django.urls import path
from . import views

urlpatterns = [
    path("<int:review_pk>", views.ProductReviewDetail.as_view()),
    path("products/<int:pk>", views.ProductReviews.as_view()),
    path(
        "<int:review_pk>/reply",
        views.ProductReviewResponse.as_view(),
    ),
    path("products/<int:pk>/images", views.ReviewImageList.as_view()),
    # SHOP
    path("<int:pk>/reviews", views.ShopReviews.as_view(), name="shop_reviews"),
    path(
        "<int:pk>/reviews/images/<int:product_pk>",
        views.ReviewPhotos.as_view(),
        name="review_photos",
    ),
]
