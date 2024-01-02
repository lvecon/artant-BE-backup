from time import sleep
from django.db.models import Count
from django.db.models import F
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from shops.models import Shop, Section
from products.models import Product
from . import serializers
from reviews.serializers import ReviewSerializer
from products.serializers import (
    ProductListSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
)


# Index page 상단. 상점 banner 정보
class ShopBanners(APIView):
    def get(self, request):
        # star seller, 최신순 정렬. 8개. TODO: 정렬 기준 논의. 현재 배경사진 있는 것만 필터링
        page_size = settings.SHOP_BANNER_PAGE_SIZE
        sorted_shops = Shop.objects.filter(background_pic__isnull=False).order_by(
            "-is_star_seller", "-created_at"
        )[0:page_size]

        serializer = serializers.ShopBannerSerializer(sorted_shops, many=True)
        return Response(serializer.data)


# Index page의 artant측 추천 판매자
class FeaturedShops(APIView):
    def get(self, request):
        # star seller, 최신순 정렬. 4개. TODO: 정렬 기준 논의. 현재 avatar 있는 것만 필터링
        page_size = settings.FEATURED_SHOP_PAGE_SIZE
        sorted_shops = Shop.objects.filter(avatar__isnull=False).order_by(
            "-is_star_seller", "-created_at"
        )[0:page_size]

        serializer = serializers.FeaturedShopSerializer(sorted_shops, many=True)
        return Response(serializer.data)


# Profile page. 당신이 좋아할 것 같은 상점. TODO: 추천 로직 추가.
class RecommendedShops(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page_size = settings.RECOMMENDED_SHOP_PAGE_SIZE
        sorted_shops = (
            Shop.objects.annotate(product_count=Count("products"))  # 상점별 상품 개수를 계산합니다.
            .filter(
                avatar__isnull=False, product_count__gt=0
            )  # avatar가 있고, 상품 개수가 0보다 큰 상점 필터링
            .order_by("-is_star_seller", "-created_at")[:page_size]
        )

        serializer = serializers.RecommendedShopSerializer(sorted_shops, many=True)
        return Response(serializer.data)


# 상점 등록 절차. 상점 등록 페이지에서 처음 생성 시, 상점 이름만 입력
class Shops(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # user의 상점 소유 여부 확인
        if hasattr(request.user, "shop"):
            return Response(
                {"error": "You already have a shop."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # user와 register_step은 시리얼라이저에서 자동 처리
        serializer = serializers.ShopCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 상점 상세 조회, 수정, 삭제 담당
class ShopDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

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

    def patch(self, request, pk):
        shop = self.get_object(pk)
        if shop.user != request.user:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = serializers.ShopUpdateSerializer(
            shop, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        shop = self.get_object(pk, request.user)
        shop.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopProducts(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            raise NotFound

    # 특정 상점의 상품 목록 가져오기. query_params: section, pagination
    def get(self, request, shop_pk):
        shop = self.get_object(shop_pk)
        products = shop.products.all()

        # 섹션 제목 기반 필터링
        section_title = request.query_params.get("section")
        if section_title == "모든 작품":
            # 모든 상품을 반환합니다
            pass
        elif section_title == "할인 중":
            # 할인 중인 상품만 필터링합니다 TODO: is_discount field 추가되면 수정
            products = products.filter(original_price__gt=F("price"))
        elif section_title:
            section = shop.sections.filter(title=section_title).first()
            if section:
                products = products.filter(section=section)
            else:
                return Response(
                    {"error": "section not found"}, status=status.HTTP_400_BAD_REQUEST
                )

        # 페이지네이션
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

    # 상점 등록
    def post(self, request, shop_pk):
        user = request.user

        # 상점 소유 여부 확인
        if user.shop.pk != shop_pk:
            return Response(
                {"error": "You do not own this shop."}, status=status.HTTP_403_FORBIDDEN
            )

        # 요청 데이터에 상점 ID 추가
        data = request.data.copy()
        data["shop"] = shop_pk

        # 상품 생성 시리얼라이저 호출
        serializer = ProductCreateSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def create_variations(self, variations_data, product):
    #     for index, variation_data in enumerate(variations_data, start=1):
    #         variation = Variation.objects.create(
    #             name=variation_data["name"],
    #             product=product,
    #             is_sku_vary=variation_data["is_sku_vary"],
    #             is_price_vary=variation_data.get("is_price_vary", False),
    #             is_quantity_vary=variation_data.get("is_quantity_vary", False),
    #             order=index,
    #         )
    #         for index, option_data in enumerate(
    #             variation_data.get("options", []), start=1
    #         ):
    #             VariationOption.objects.create(
    #                 name=option_data["name"],
    #                 variation=variation,
    #                 order=index,
    #             )

    # def create_variants(self, variants_data, product):
    #     for index, variant_data in enumerate(variants_data, start=1):
    #         option_one, option_two = self.get_variant_options(variant_data, product)
    #         ProductVariant.objects.create(
    #             product=product,
    #             option_one=option_one,
    #             option_two=option_two,
    #             sku=variant_data.get("sku", ""),
    #             price=variant_data.get("price", 0),
    #             quantity=variant_data.get("quantity", 0),
    #             is_visible=variant_data.get("is_visible", True),
    #             order=index,
    #         )

    # def get_variant_options(self, variant_data, product):
    #     option_one = self.get_option(variant_data.get("option_one"), product)
    #     option_two = self.get_option(variant_data.get("option_two"), product)
    #     return option_one, option_two

    # def get_option(self, option_name, product):
    #     if option_name:
    #         return VariationOption.objects.filter(
    #             name=option_name,
    #             variation__product=product,
    #         ).first()


# 상점의 상품 정보 업데이트
class ShopProductUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def get_product(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

    # 상품 상제 정보. 상품 업데이트 페이지.
    def get(self, request, shop_pk, product_pk):
        # 상점이 존재하며 요청한 사용자가 상점의 소유자인지 확인
        shop = get_object_or_404(Shop, pk=shop_pk, user=request.user)

        # 상품이 해당 상점에 속해 있는지 확인
        product = get_object_or_404(Product, pk=product_pk, shop=shop)

        serializer = ProductUpdateSerializer(
            product,
            context={"reqeust": request},
        )
        return Response(serializer.data)

    def patch(self, request, shop_pk, product_pk):
        # 상점이 존재하며 요청한 사용자가 상점의 소유자인지 확인
        shop = get_object_or_404(Shop, pk=shop_pk, user=request.user)

        # 상품이 해당 상점에 속해 있는지 확인
        product = get_object_or_404(Product, pk=product_pk, shop=shop)

        serializer = ProductUpdateSerializer(
            product, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 상품 생성 Or 편집 화면에서 section 생성 TODO: ShopDetail 의 PATCH에서 해결 가능. 삭제 고려
class ShopSections(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_pk):
        # 상점 존재 여부 확인
        try:
            shop = Shop.objects.get(pk=shop_pk)
        except Shop.DoesNotExist:
            raise NotFound("Shop not found")

        serializer = serializers.ShopSectionSerializer(
            shop, context={"request": request}
        )

        return Response(serializer.data)

    # TODO: 상점 PATCH API로 해결됨. 삭제 고려
    # def post(self, request, shop_pk):
    #     user = request.user
    #     # 사용자가 해당 상점의 소유자인지 확인
    #     if not user.shop.pk == shop_pk:
    #         return Response(
    #             {"error": "You do not own this shop."}, status=status.HTTP_403_FORBIDDEN
    #         )

    #     serializer = serializers.SectionSerializer(data=request.data)
    #     if serializer.is_valid():
    #         # 동일한 제목의 섹션이 이미 있는지 확인
    #         if Section.objects.filter(
    #             shop_id=shop_pk, title=serializer.validated_data["title"]
    #         ).exists():
    #             return Response(
    #                 {"error": "A section with this title already exists."},
    #                 status=status.HTTP_400_BAD_REQUEST,
    #             )

    #         # 새 섹션 생성
    #         section = serializer.save(shop_id=shop_pk)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
