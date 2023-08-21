from django.urls import path
from .views import CartView, CartLineView

urlpatterns = [
    path("", CartView.as_view()),
    path("<int:cartline_pk>", CartLineView.as_view()),
]
