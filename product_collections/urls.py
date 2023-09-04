from django.urls import path
from .views import ProductCollectionView

urlpatterns = [
    path("", ProductCollectionView.as_view()),
]
