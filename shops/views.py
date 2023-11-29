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

from shops.models import Shop, Section
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
from favorites.serializers import FavoriteShopSerializer


# Index page의 상점 banner 정보
class ShopBanners(APIView):
    def get(self, request):
        # star seller, 최신순 정렬. 8개. TODO: 정렬 기준 논의. 현재 배경사진 있는 것만 필터링
        page_size = settings.SHOP_BANNER_PAGE_SIZE
        sorted_shops = Shop.objects.filter(background_pic__isnull=False).order_by(
            "-is_star_seller", "-created_at"
        )[0:page_size]

        serializer = serializers.ShopBannerSerializer(sorted_shops, many=True)
        return Response(serializer.data)


# Index page의 추천 판매자
class FeaturedShops(APIView):
    def get(self, request):
        # star seller, 최신순 정렬. 4개. TODO: 정렬 기준 논의. 현재 avatar 있는 것만 필터링
        page_size = settings.SHOP_ARTIST_PAGE_SIZE
        sorted_shops = Shop.objects.filter(avatar__isnull=False).order_by(
            "-is_star_seller", "-created_at"
        )[0:page_size]

        serializer = serializers.RecommendedShopSerializer(sorted_shops, many=True)
        return Response(serializer.data)


class Shops(APIView):
    def get(self, request):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.SHOP_ARTIST_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        sorted_shops = Shop.objects.order_by("-is_star_seller", "-created_at")[
            start:end
        ]

        serializer = FavoriteShopSerializer(sorted_shops, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)  # 권한 확인

        # user의 상점 소유 여부 확인
        if hasattr(request.user, "shop"):
            return Response(
                {"error": "You already have a shop."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data["user"] = request.user.id  # 현재 사용자를 상점 소유자로 설정

        if "register_step" in data:
            # Existing shop, update step
            shop = request.user.shop
            serializer = serializers.ShopCreateSerializer(shop, data=data)
        else:
            # New shop creation
            data["register_step"] = 1  # Starting from step 1
            serializer = serializers.ShopCreateSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        try:
            shop = Shop.objects.get(id=request.data["id"], user=request.user)
        except Shop.DoesNotExist:
            return Response(
                {"error": "Shop not found or not owned by user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data.copy()
        data[
            "user"
        ] = request.user.id  # Ensure the shop is still owned by the request user
        data["shop_name"] = shop.shop_name
        serializer = serializers.ShopUpdateSerializer(shop, data=data)
        print(serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# TODO: Update 전용 serializer 생성. shop model 이미지 필드들 따로 모델 만들어서 구현하기!
class ShopUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            shop = Shop.objects.get(pk=pk, user=request.user)
        except Shop.DoesNotExist:
            return Response(
                {
                    "error": "Shop not found or you do not have permission to edit this shop."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = serializers.ShopSerializer(shop, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        products = shop.products.all()
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
        products = shop.products.all()

        # 섹션 제목 기반 필터링
        section_title = request.query_params.get("section")
        if section_title:
            sections = Section.objects.filter(title=section_title, shop=shop)
            if sections.exists():
                products = products.filter(section__in=sections)

        try:
            page = int(request.query_params.get("page", 1))
        except ValueError:
            page = 1

        page_size = settings.SHOP_PRODUCT_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        total_count = products.count()  # Get the total count of products

        serializer = ProductListSerializer(
            products[start:end],
            many=True,
            context={"request": request},
        )

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

        products = shop.products.all()
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

        # 섹션 처리
        section_title = request.data.get("section")
        if section_title:
            section, created = Section.objects.get_or_create(
                title=section_title, shop_id=shop_pk
            )
            data["section"] = section.pk

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


# 상품 생성 Or 편집 화면에서 section 생성
class CreateSection(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shop_pk):
        user = request.user
        # 사용자가 해당 상점의 소유자인지 확인
        if not user.shop.pk == shop_pk:
            return Response(
                {"error": "You do not own this shop."}, status=status.HTTP_403_FORBIDDEN
            )

        section_title = request.data.get("section")
        if not section_title:
            return Response(
                {"error": "Section title is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 동일한 제목의 섹션이 이미 있는지 확인
        if Section.objects.filter(shop_id=shop_pk, title=section_title).exists():
            return Response(
                {"error": "A section with this title already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 새 섹션 생성
        section = Section.objects.create(title=section_title, shop_id=shop_pk)

        serializer = serializers.SectionSerializer(section)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
