from django.urls import path
from . import views


urlpatterns = [
    path("", views.Products.as_view()),
    path("<int:pk>", views.ProductDetails.as_view()),
    path("<int:pk>/reviews", views.ProductReviews.as_view()),
    path("<int:pk>/reviews/<int:review_pk>", views.ProductReviewDetail.as_view()),
    path(
        "<int:pk>/reviews/<int:review_pk>/reply",
        views.ProductReviewReply.as_view(),
    ),
    path("recently-viewed", views.RecentlyViewed.as_view()),
    path("photos/<int:pk>", PhotoDetail.as_view()),
    path("photos/get-url", GetUploadURL.as_view()),
    path("videos/get-url", GetVideoUploadURL.as_view()),
]
