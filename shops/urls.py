from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create your views here.
urlpatterns = [
    path("", views.Shops.as_view()),
    path("<int:pk>", views.ShopDetail.as_view()),
    path("<int:pk>/reviews", views.ShopReviews.as_view()),
    path("<int:pk>/reviews/images/<int:product_pk>", views.ReviewPhotos.as_view()),
    path("<int:pk>/products", views.ShopProducts.as_view()),
    path("<int:shop_pk>/create-product", views.CreateProduct.as_view()),
    path("<int:shop_pk>/create-section", views.CreateSection.as_view()),
]
