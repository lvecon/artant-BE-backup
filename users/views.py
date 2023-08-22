from time import sleep
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated

from users.models import Shop, User
from products.models import Product
from reviews.models import Review
from . import serializers
from reviews.serializers import ReviewSerializer, ReviewDetailSerializer
from products.serializers import ProductListSerializer


class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            user = serializer.save()
            serializer = serializers.PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class Users(APIView):
    def post(self, request):
        password = request.data.get("password")
        if not password:
            raise ParseError
        serializer = serializers.PrivateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()
            serializer = serializers.PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PublicUser(APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise ParseError
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            raise ParseError


class LogIn(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return Response({"ok": "Welcome!"})
        else:
            return Response(
                {"error": "wrong password"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sleep(5)
        logout(request)
        return Response({"ok": "bye!"})


class Shops(APIView):
    def get(self, request):
        sorted_shops = Shop.objects.order_by("-is_star_seller", "-created_at")

        serializer = serializers.TinyShopSerializer(sorted_shops, many=True)
        return Response(serializer.data)


class ShopDetail(APIView):
    def get_object(self, pk):
        try:
            return Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        shop = self.get_object(pk)

        serializer = serializers.ShopDetailSerializer(
            shop,
            context={"reqeust": request},
        )
        return Response(serializer.data)


class ShopReviews(APIView):
    def get_object(self, pk):
        try:
            return Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1
        query_type = self.request.GET.get("sort", None)
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        shop = self.get_object(pk)

        products = shop.product.all()
        all_reviews = []
        for product in products:
            reviews = product.reviews.all()
            all_reviews.extend(reviews)

        total_reviews = len(all_reviews)

        if query_type == "created_at":
            all_reviews_sorted = sorted(
                all_reviews, key=lambda x: x.created_at, reverse=True
            )
            serializer = ReviewSerializer(
                all_reviews_sorted[start:end],
                many=True,
            )

            response_data = {
                "total_count": total_reviews,  # 상품의 총 개수를 응답 데이터에 추가
                "reviews": serializer.data,
            }

            return Response(response_data)

        else:  # suggested
            all_reviews = sorted(
                all_reviews,
                key=lambda x: (
                    len(x.content),
                    x.rating * 100 + x.images.count() * 40,
                ),
                reverse=True,
            )
            serializer = ReviewSerializer(
                all_reviews[start:end],
                many=True,
            )

            response_data = {
                "total_count": total_reviews,
                "reviews": serializer.data,
            }
            return Response(response_data)


class ShopProducts(APIView):
    def get_object(self, pk):
        try:
            return Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        shop = self.get_object(pk)
        products = shop.product.all()

        serializer = ProductListSerializer(
            products,
            many=True,
            context={"reqeust": request},
        )
        return Response(serializer.data)


class ReviewPhotos(APIView):
    def get_object(self, pk):
        try:
            return Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            raise NotFound

    def get(self, request, pk, product_pk):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.REVIEW_IMAGE_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        shop = self.get_object(pk)
        product_name = Product.objects.get(pk=product_pk).name

        products = shop.product.all()
        all_reviews = []
        for product in products:
            reviews = product.reviews.filter(images__isnull=False)
            all_reviews.extend(reviews)

        all_reviews_sorted = sorted(
            all_reviews, key=lambda x: x.created_at, reverse=True
        )

        same_product_reviews = []
        other_reviews = []
        for review in all_reviews_sorted:
            if review.product.name == product_name:
                same_product_reviews.append(review)
            else:
                other_reviews.append(review)

        all_reviews_with_images = same_product_reviews + other_reviews

        images = [
            image.image
            for review in all_reviews_with_images
            for image in review.images.all()
        ][start:end]

        response_data = {
            "images": images,
        }
        return Response(response_data)
