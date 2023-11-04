from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Count
from .models import Collection
from products.models import Product
from .serializers import CollectionSerializer


class ProductCollectionView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        collections = Collection.objects.all()  # 모든 Collection 가져오기

        serializer = CollectionSerializer(
            collections,
            many=True,  # 여러 개의 Collection을 직렬화해야 함을 명시
            context={"request": request},
        )
        return Response(serializer.data)
