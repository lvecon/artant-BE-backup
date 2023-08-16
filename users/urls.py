from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create your views here.
urlpatterns = [
    path("", views.Users.as_view()),
    path("me", views.Me.as_view()),
    path("change-password", views.ChangePassword.as_view()),
    path("log-in", views.LogIn.as_view()),
    path("log-out", views.LogOut.as_view()),
    path("@<str:username>", views.PublicUser.as_view()),
    path("shop", views.Shops.as_view()),
    path("shop/<int:pk>", views.ShopDetail.as_view()),
    path("shop/<int:pk>/reviews", views.ShopReviews.as_view()),
    path("shop/<int:pk>/reviews/images/<int:product_pk>", views.ReviewImages.as_view()),
    path("shop/<int:pk>/products", views.ShopProducts.as_view()),
]
