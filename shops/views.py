from time import sleep
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from users.models import User
from shops.models import Shop
from products.models import (
    Product,
    Color,
)
from product_attributes.models import Category, Material, ProductTag
from product_variants.models import ProductVariant, Variation, VariationOption
from reviews.models import Review
from . import serializers
from reviews.serializers import ReviewSerializer, ReviewDetailSerializer
from products.serializers import ProductListSerializer, ProductCreateSerializer


class Shops(APIView):
    def get(self, request):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.ARTIST_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        sorted_shops = Shop.objects.order_by("-is_star_seller", "-created_at")[
            start:end
        ]

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
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.SHOP_PRODUCT_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        shop = self.get_object(pk)
        products = shop.product.all()

        total_count = products.count()  # Get the total count of products

        serializer = ProductListSerializer(
            products[start:end],
            many=True,
            context={"reqeust": request},
        )

        # Create a dictionary containing 'total_counts' along with serialized data
        response_data = {
            "total_count": total_count,
            "products": serializer.data,
        }

        return Response(response_data)


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


class CreateProduct(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request, shop_pk):
        user = request.user
        # 사용자의 상점과 요청된 상점 ID가 일치하는지 확인
        if not user.shop.pk == shop_pk:
            return Response(
                {"error": "You do not own this shop."}, status=status.HTTP_403_FORBIDDEN
            )

        category_name = request.data.get("category_name")
        # 카테고리 이름으로 카테고리 객체를 가져옴, 없으면 404 응답
        category = get_object_or_404(Category, name=category_name)

        # 요청 데이터에서 primary_color와 secondary_color 값을 가져옵니다.
        primary_color_name = request.data.get("primary_color")
        secondary_color_name = request.data.get("secondary_color")

        # 색상 객체들을 검색합니다. 색상이 없으면 None을 반환합니다.
        primary_color = Color.objects.filter(name=primary_color_name).first()
        secondary_color = Color.objects.filter(name=secondary_color_name).first()

        if primary_color_name and not primary_color:
            return Response(
                {"primary_color": "Invalid primary color"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if secondary_color_name and not secondary_color:
            return Response(
                {"secondary_color": "Invalid secondary color"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data["shop"] = shop_pk

        serializer = ProductCreateSerializer(data=data)

        if serializer.is_valid():
            product = serializer.save()  # 상품을 저장합니다.

            # Variation 처리
            variation_instances = {}
            variations_data = request.data.get("variations", [])
            for variation_data in variations_data:
                variation = Variation.objects.create(
                    name=variation_data["name"],
                    product=product,
                    is_sku_vary=variation_data["is_sku_vary"],
                    is_price_vary=variation_data.get("is_price_vary", False),
                    is_quantity_vary=variation_data.get("is_quantity_vary", False),
                )
                variation_instances[variation.name] = variation

                for option_data in variation_data.get("options", []):
                    VariationOption.objects.create(
                        name=option_data["name"], variation=variation
                    )

            # ProductVariant 처리
            variants_data = request.data.get("variants", [])
            for variant_data in variants_data:
                option_one = None
                option_two = None

                # option_one 찾기
                if variant_data.get("option_one"):
                    option_one = VariationOption.objects.filter(
                        name=variant_data.get("option_one"),
                        variation__in=variation_instances.values(),
                    ).first()

                # option_two 찾기
                if variant_data.get("option_two"):
                    option_two = VariationOption.objects.filter(
                        name=variant_data.get("option_two"),
                        variation__in=variation_instances.values(),
                    ).first()

                ProductVariant.objects.create(
                    product=product,
                    option_one=option_one,
                    option_two=option_two,
                    sku=variant_data.get("sku", ""),
                    price=variant_data.get("price", 0),
                    quantity=variant_data.get("quantity", 0),
                    is_visible=variant_data.get("is_visible", True),
                )

            materials_data = request.data.get("materials", [])  # 재료 이름 목록을 받음
            for material_name in materials_data:
                material, created = Material.objects.get_or_create(name=material_name)
                product.materials.add(material)

            # 태그 처리
            tags_data = request.data.get("tags", [])  # 사용자가 제공한 태그 목록
            for tag_name in tags_data:
                tag, created = ProductTag.objects.get_or_create(tag=tag_name)
                product.tags.add(tag)

            product.category.add(category.id)
            if primary_color:
                product.primary_color = primary_color
            if secondary_color:
                product.secondary_color = secondary_color
            product.save()

            if category.parent:
                product.category.add(category.parent.id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShopCreate(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능하도록 설정

    def post(self, request):
        data = request.data.copy()
        data["users"] = [request.user.id]  # 현재 사용자를 상점 소유자로 설정

        serializer = serializers.ShopCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
