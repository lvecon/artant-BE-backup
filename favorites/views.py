from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FavoritesItem
from .serializer import FavoriteItemSerializer

# Create your views here.


class FavoritesItems(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_favorites_items = FavoritesItem.objects.all()
        serializer = FavoriteItemSerializer(all_favorites_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        pass

    def delete(self, request):
        pass
