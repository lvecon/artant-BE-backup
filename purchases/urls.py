from django.urls import path
from .views import PurchaseView, PurchaseLineView

urlpatterns = [
    path("", PurchaseView.as_view()),
    path("<int:purchaseline_pk>", PurchaseLineView.as_view()),
]
