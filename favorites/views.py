from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
)
from products.models import Product
from users.models import Shop
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
        serializer = TinyFavoriteItemSerializer(
            all_favorites_items,
            many=True,
            context={"request": request},
        )
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
        serializer = FavoriteItemSerializer(
            favorite_items,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        serializer = TinyFavoriteItemSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            favorite_item = serializer.save()

        pass

    def delete(self, request):
        pass


class FavoriteItemToggle(APIView):
    def get_favoriteItems(self, user):
        try:
            return FavoriteItem.objects.get(user=user)
        except FavoriteItem.DoesNotExist:
            raise NotFound

    def get_product(self, product_pk):
        try:
            return Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            raise NotFound

    def put(self, request, product_pk):
        favorite_item_list = self.get_favoriteItems(request.user)
        product = self.get_product(product_pk)
        if favorite_item_list.products.filter(pk=product_pk).exists():
            favorite_item_list.products.remove(product)
        else:
            favorite_item_list.products.add(product)
        return Response(status=HTTP_200_OK)


class FavoritesShops(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_favorite_shops = FavoriteShop.objects.all()
        serializer = TinyFavoriteShopSerializer(
            all_favorite_shops,
            many=True,
            context={"request": request},
        )
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
        serializer = FavoriteShopSerializer(
            favorite_shops,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        pass

    def delete(self, request):
        pass


class FavoriteShopToggle(APIView):
    def get_favoriteShops(self, user):
        try:
            return FavoriteShop.objects.get(user=user)
        except FavoriteShop.DoesNotExist:
            raise NotFound

    def get_shop(self, shop_pk):
        try:
            return Shop.objects.get(pk=shop_pk)
        except Shop.DoesNotExist:
            raise NotFound

    def put(self, request, shop_pk):
        favorite_shop_list = self.get_favoriteShops(request.user)
        shop = self.get_shop(shop_pk)
        if favorite_shop_list.shops.filter(pk=shop_pk).exists():
            favorite_shop_list.shops.remove(shop)
        else:
            favorite_shop_list.shops.add(shop)
        return Response(status=HTTP_200_OK)
