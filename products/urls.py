from django.urls import path
from . import views
from common.views import GetUploadURL, GetVideoUploadURL


urlpatterns = [
    path("", views.Products.as_view()),
    path("<int:pk>", views.ProductDetails.as_view()),
    path("<int:pk>/reviews", views.ProductReviews.as_view()),
    path("<int:pk>/reviews/<int:review_pk>", views.ProductReviewDetail.as_view()),
    path(
        "<int:pk>/reviews/<int:review_pk>/reply",
        views.ProductReviewReply.as_view(),
    ),
    path("<int:product_pk>/reviews/photos", views.ReviewPhotoList.as_view()),
    path("<int:pk>/photos", views.ProductImages.as_view()),
    path("<int:pk>/videos", views.ProductVideos.as_view()),
    path("photos/<int:pk>", views.PhotoDetail.as_view()),
    path("photos/get-url", GetUploadURL.as_view()),
    path("videos/get-url", GetVideoUploadURL.as_view()),
    path("edit-product/<int:product_pk>", views.EditProduct.as_view()),
]
