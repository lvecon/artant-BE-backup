# 표준 라이브러리
from django.utils.timezone import now
from django.db.models import Count, Q


# Django 관련 라이브러리
from django.conf import settings
from django.db.models import Q

# 서드파티 라이브러리
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status
from rest_framework.status import HTTP_200_OK

# 로컬 애플리케이션 모듈
from products.models import Product, ProductImage
from . import serializers
from reviews.serializers import (
    ReviewSerializer,
    ReviewImageSerializer,
    ReviewResponseSerializer,
)
from reviews.models import Review, ReviewResponse, ReviewImage
from user_activities.models import UserProductTimestamp


class Products(APIView):
    def get_query_params(self):
        return {
            "color_param": self.request.GET.get("color", None),
            "limit": int(self.request.GET.get("limit", 40)),
            "offset": int(self.request.GET.get("offset", 0)),
            "category_type": self.request.GET.get("category", None),
            "tag": self.request.GET.get("tag", None),
            "price_upper_range": self.request.GET.get("PriceUpper", 10000000),
            "price_lower_range": self.request.GET.get("PriceLower", 0),
            "search": self.request.GET.get("search", None),
            "query_type": self.request.GET.get("sort", None),
        }

    def get_products_query(self, params):
        q = Q()
        if params["color_param"]:
            colors = params["color_param"].split(",")
            color_query = Q(primary_color__name__in=colors) | Q(
                secondary_color__name__in=colors
            )
            q &= color_query

        if params["category_type"] and params["category_type"] != "모든작품":
            q &= Q(category__name=params["category_type"])

        if params["tag"]:
            q &= Q(tags__name=params["tag"])

        if params["price_lower_range"] != 0 or params["price_upper_range"] != 10000000:
            q &= Q(
                price__range=(params["price_lower_range"], params["price_upper_range"])
            )

        if params["search"]:
            q &= (
                Q(name__icontains=params["search"])
                | Q(description__icontains=params["search"])
                | Q(shop__shop_name__exact=params["search"])
            )

        return q

    def get_sorted_products(self, products, query_type, offset, limit):
        if query_type == "created_at":
            return products.order_by("-created_at")[offset : offset + limit]
        elif query_type == "price_asc":
            return products.order_by("price")[offset : offset + limit]
        elif query_type == "price_desc":
            return products.order_by("-price")[offset : offset + limit]
        elif query_type == "discount_desc":
            return products.order_by("-discount_rate")[offset : offset + limit]
        elif query_type == "review_desc":
            return products.annotate(review_count=Count("reviews")).order_by(
                "-review_count"
            )[offset : offset + limit]
        else:
            return products.order_by("-order_count")[offset : offset + limit]

    def get(self, request):
        params = self.get_query_params()
        q = self.get_products_query(params)
        products = Product.objects.filter(q).distinct()
        total_products = products.count()

        sorted_products = self.get_sorted_products(
            products, params["query_type"], params["offset"], params["limit"]
        )
        serializer = serializers.ProductListSerializer(
            sorted_products,
            many=True,
            context={"request": request},
        )

        response_data = {
            "total_count": total_products,
            "products": serializer.data,
        }
        print(self.request.session.session_key)

        return Response(response_data)


# 상품 페이지
class ProductDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 유저의 최근 본 상품 기록 추가
    def user_viewed(self, timestamp, product):
        user = self.request.user
        if not user.is_authenticated:
            viewed_products = self.request.session.get("viewed_products", [])

            product_exists = False
            for view in viewed_products:
                if view["product_id"] == product.id:
                    # Update the timestamp of the existing product
                    view["timestamp"] = now().isoformat()
                    product_exists = True
                    break

            if not product_exists:
                # Add the new product with its timestamp
                viewed_products.append(
                    {"product_id": product.id, "timestamp": now().isoformat()}
                )

            # Store the updated list in the session
            self.request.session["viewed_products"] = viewed_products
            self.request.session.save()

            return
        upt, _ = UserProductTimestamp.objects.get_or_create(user=user, product=product)
        upt.timestamp = timestamp
        upt.save()
        return upt.timestamp

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        product = self.get_object(pk)
        # 상품 조회 시, 최근 본 상품 추가
        self.user_viewed(now(), product)
        serializer = serializers.ProductDetailSerializer(
            product,
            context={"reqeust": request},
        )
        return Response(serializer.data)


class ProductImages(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound("Product not found")

    def post(self, request, pk):
        product = self.get_product(pk)

        # 상품 소유권 확인
        if hasattr(request.user, "shop") and request.user.shop != product.shop:
            raise PermissionDenied(
                "You do not have permission to add images to this product"
            )

        # 이미지 추가
        serializer = serializers.ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductVideos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        product = self.get_object(pk)

        # if request.user != room.owner:
        #     raise PermissionDenied
        serializer = serializers.VideoSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save(product=product)  # connect to room
            serializer = serializers.VideoSerializer(video)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
