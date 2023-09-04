from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Collection


class CollectionSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ("id", "title", "contents", "thumbnails", "total_products")

    def get_thumbnails(self, obj):
        # Collection에 속한 최대 4개의 Product 썸네일을 가져옵니다.
        products = obj.product.all()[:4]  # 최대 4개의 Product 가져오기
        thumbnails = [product.thumbnail for product in products]
        return thumbnails

    def get_total_products(self, obj):
        # Collection에 속한 Product들의 총 개수를 반환합니다.
        return obj.product.count()
