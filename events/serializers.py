from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from favorites.models import FavoriteItem
from .models import Event, EventImage


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ("pk", "image")


class EventSerializer(ModelSerializer):
    image = EventImageSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = (
            "title",
            "contents",
            "image",
        )
