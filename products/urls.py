from django.urls import path
from . import views
from common.views import GetUploadURL, GetVideoUploadURL


urlpatterns = [
    path("", views.Products.as_view(), name="products"),
    path("<int:pk>", views.ProductDetail.as_view(), name="product_detail"),
    # TODO: reviews APP으로 이동. image, video 관련 API는  불필요하므로 삭제 고려.
    path("<int:pk>/reviews", views.ProductReviews.as_view()),
    path("<int:pk>/reviews/<int:review_pk>", views.ProductReviewDetail.as_view()),
    path(
        "<int:pk>/reviews/<int:review_pk>/reply",
        views.ProductReviewResponse.as_view(),
    ),
    path("<int:product_pk>/reviews/images", views.ReviewImageList.as_view()),
    path("<int:pk>/images", views.ProductImages.as_view()),
    path("<int:pk>/videos", views.ProductVideos.as_view()),
    path("images/<int:pk>", views.ProductImageDetail.as_view()),
]
