from rest_framework.serializers import ModelSerializer
from .models import FavoritesItem


class FavoriteItemSerializer(ModelSerializer):
    class Meta:
        model = FavoritesItem
        fields = "__all__"
