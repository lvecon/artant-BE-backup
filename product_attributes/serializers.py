from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import ProductTag, Color


class ProductTagSerializer(ModelSerializer):
    class Meta:
        model = ProductTag
        fields = "__all__"


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ("pk", "name")
