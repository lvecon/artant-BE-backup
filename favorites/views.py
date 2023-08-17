from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
)
from .models import FavoriteItem, FavoriteShop
from .serializer import (
    FavoriteItemSerializer,
    TinyFavoriteItemSerializer,
    TinyFavoriteShopSerializer,
    FavoriteShopSerializer,
)

# Create your views here.


class FavoritesItems(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_favorites_items = FavoriteItem.objects.all()
        serializer = TinyFavoriteItemSerializer(all_favorites_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        pass

    def delete(self, request):
        pass


class UserFavoritesItems(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return FavoriteItem.objects.get(user_id=pk)
        except FavoriteItem.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        favorite_items = self.get_object(pk)
        serializer = FavoriteItemSerializer(favorite_items)
        return Response(serializer.data)

    def post(self, request):
        pass

    def delete(self, request):
        pass


class FavoritesShops(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_favorite_shops = FavoriteShop.objects.all()
        serializer = TinyFavoriteShopSerializer(all_favorite_shops, many=True)
        return Response(serializer.data)

    def post(self, request):
        pass

    def delete(self, request):
        pass


class UserFavoritesShops(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return FavoriteShop.objects.get(user_id=pk)
        except FavoriteShop.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        favorite_shops = self.get_object(pk)
        serializer = FavoriteShopSerializer(favorite_shops)
        return Response(serializer.data)

    def post(self, request):
        pass

    def delete(self, request):
        pass
