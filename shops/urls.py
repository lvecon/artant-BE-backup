from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    # 상점 등록. 상점 목록 및 관련 상점 정보 조회
    path("", views.Shops.as_view(), name="shops"),
    path("banners", views.ShopBanners.as_view(), name="shop_banners"),
    path("featured-shops", views.FeaturedShops.as_view(), name="featured_shops"),
    path(
        "recommended-shops", views.RecommendedShops.as_view(), name="recommended_shops"
    ),
    # 특정 상점에 대한 상세 정보 및 관리
    path("<int:pk>", views.ShopDetail.as_view(), name="shop_detail"),
    path("<int:pk>/reviews", views.ShopReviews.as_view(), name="shop_reviews"),
    path(
        "<int:pk>/reviews/images/<int:product_pk>",
        views.ReviewPhotos.as_view(),
        name="review_photos",
    ),
    # 특정 상점의 제품 및 섹션 관리
    path(
        "<int:shop_pk>/products",
        views.ShopProducts.as_view(),
        name="shop_products_list",
    ),
    path(
        "<int:shop_pk>/products/<int:product_pk>",
        views.ProductUpdate.as_view(),
        name="product_update",
    ),
    path("<int:shop_pk>/sections", views.Sections.as_view(), name="shop_sections"),
]
