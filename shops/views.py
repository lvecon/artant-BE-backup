from time import sleep
from django.db.models import Count
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from shops.models import Shop, Section, ShopImage
from products.models import Product, Color, ProductImage
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


# Profile page. 당신이 좋아할 것 같은 상점. TODO: 추천 로직 추가. permission class 설정.
class RecommendedShops(APIView):
    def get(self, request):
        page_size = settings.RECOMMENDED_SHOP_PAGE_SIZE
        sorted_shops = (
            Shop.objects.annotate(product_count=Count("products"))  # 상점별 상품 개수를 계산합니다.
            .filter(
                avatar__isnull=False, product_count__gt=0
            )  # avatar가 있고, 상품 개수가 0보다 큰 상점 필터링
            .order_by("-is_star_seller", "-created_at")[:page_size]
        )

        serializer = FavoriteShopSerializer(sorted_shops, many=True)
        return Response(serializer.data)


class Shops(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # user의 상점 소유 여부 확인
        if hasattr(request.user, "shop"):
            return Response(
                {"error": "You already have a shop."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data
        data["user"] = request.user.id  # 현재 사용자를 상점 소유자로 설정
        data["register_step"] = data.get("register_step", 1)
        serializer = serializers.ShopCreateSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        sections_data = request.data.get('sections')
        if sections_data:
            # 섹션의 title 중복 확인 TODO: 프론트에서 확인할지 논의
            titles = [section.get('title') for section in sections_data]
            if len(titles) != len(set(titles)):
                return Response(
                    {"error": "Duplicate section titles found."},
                    status=status.HTTP_400_BAD_REQUEST,
            )
        images_data = request.data.get('images')
       
        serializer = serializers.ShopUpdateSerializer(shop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            #섹션 정보 업데이트 (sections 키가 있는 경우에만)
            if sections_data is not None:
                self.update_sections(sections_data, shop)

            if images_data is not None:
                self.update_images(images_data, shop)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        shop = self.get_object(pk, request.user)
        shop.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

    def update_sections(self, sections_data, shop):
        existing_sections = {section.title: section for section in shop.sections.all()}
        updated_sections = set()

        for section_data in sections_data:
            section_title = section_data.get("title")
            # TODO: 기존 섹션의 경우 요청에 id를 함께 보내서 이를 통해 기존 섹션인지 확인하는 방법도..
            if section_title in existing_sections:
            # 기존 섹션 업데이트
                existing_section = existing_sections[section_title]
                for key, value in section_data.items():
                    setattr(existing_section, key, value)
                existing_section.save()
                updated_sections.add(existing_section)
            else:
                # 새 섹션 추가
                new_section = Section.objects.create(**section_data, shop=shop)
                updated_sections.add(new_section)

        # 삭제되어야 하는 섹션 찾기 및 삭제. TODO: 삭제 허용에 대해 의논. 기존에 연결된 상품 어떻게 할지?
        for title, existing_section in existing_sections.items():
            if existing_section not in updated_sections:
                existing_section.delete()

    def update_images(self, images_data, shop):
        existing_images = {image.image: image for image in shop.images.all()}
        updated_images = set()

        for image_data in images_data:
            image_url = image_data.get("image")
            if image_url in existing_images:
                # 기존 이미지 업데이트
                image = existing_images[image_url]
                for key, value in image_data.items():
                    setattr(image, key, value)
                image.save()
                updated_images.add(image)
            else:
                # 새 이미지 추가
                new_image = ShopImage.objects.create(**image_data, shop=shop)
                updated_images.add(new_image)

        # 삭제되어야 하는 이미지 찾기 및 삭제
        for existing_image in existing_images.values():
            if existing_image not in updated_images:
                existing_image.delete()




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

    def get(self, request, shop_pk):
        shop = self.get_object(shop_pk)
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
    
    def post(self, request, shop_pk):
        user = request.user
        # 사용자의 상점과 요청된 상점 ID가 일치하는지 확인
        if not user.shop.pk == shop_pk:
            return Response(
                {"error": "You do not own this shop."}, status=status.HTTP_403_FORBIDDEN
            )

      
        data = request.data.copy()
        data["shop"] = shop_pk
        # 섹션 처리
        self.set_section(data, shop_pk)
        serializer = ProductCreateSerializer(data=data)
        if serializer.is_valid():
            # 카테고리 이름으로 카테고리 객체를 가져옴, 없으면 404 응답
            category_name = request.data.get("category_name")
            category = get_object_or_404(Category, name=category_name)

            # 색상 처리
            primary_color, secondary_color = self.get_colors(request)

            # 상품 저장
            product = serializer.save()
            
            # Variation 처리
            self.create_variations(
                variations_data=request.data.get("variations", []), product=product
            )
            self.create_variants(
                variants_data=request.data.get("variants", []), product=product
            )
            self.set_materials_and_tags(materials_data=request.data.get("materials", []),
                                        tags_data=request.data.get("tags", []), product=product)
            self.process_images(images_data=request.data.get("images", []), product=product)

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

    # primary color, secondary color 처리
    def get_colors(self, request):
        primary_color_name = request.data.get("primary_color")
        secondary_color_name = request.data.get("secondary_color")

        try:
            primary_color = (
                Color.objects.get(name=primary_color_name)
                if primary_color_name
                else None
            )
            secondary_color = (
                Color.objects.get(name=secondary_color_name)
                if secondary_color_name
                else None
            )
        except Color.DoesNotExist:
            raise serializers.ValidationError({"color": "Invalid color name"})

        return primary_color, secondary_color

    def set_section(self, data, shop_pk):
        section_title = data.get("section")
        if section_title:
            section, _ = Section.objects.get_or_create(
                title=section_title, shop_id=shop_pk
            )
            data["section"] = section.pk

    def create_variations(self, variations_data, product):
        for variation_data in variations_data:
            variation = Variation.objects.create(
                name=variation_data["name"],
                product=product,
                is_sku_vary=variation_data["is_sku_vary"],
                is_price_vary=variation_data.get("is_price_vary", False),
                is_quantity_vary=variation_data.get("is_quantity_vary", False),
            )
            for option_data in variation_data.get("options", []):
                VariationOption.objects.create(
                    name=option_data["name"], variation=variation
                )

    def create_variants(self, variants_data, product):
        for variant_data in variants_data:
            option_one, option_two = self.get_variant_options(variant_data, product)
            ProductVariant.objects.create(
                product=product,
                option_one=option_one,
                option_two=option_two,
                sku=variant_data.get("sku", ""),
                price=variant_data.get("price", 0),
                quantity=variant_data.get("quantity", 0),
                is_visible=variant_data.get("is_visible", True),
            )

    def get_variant_options(self, variant_data, product):
        option_one = self.get_option(variant_data.get("option_one"), product)
        option_two = self.get_option(variant_data.get("option_two"), product)
        return option_one, option_two

    def get_option(self, option_name, product):
        if option_name:
            return VariationOption.objects.filter(
                name=option_name,
                variation__product=product,
            ).first()
    def set_materials_and_tags(self, materials_data, tags_data, product):
        for material_name in materials_data:
            material, _ = Material.objects.get_or_create(name=material_name)
            product.materials.add(material)
        for tag_name in tags_data:
            tag, _ = ProductTag.objects.get_or_create(tag=tag_name)
            product.tags.add(tag)

    def process_images(self, images_data, product):
        thumbnail_url = None
        for image_data in images_data:
            image_obj = ProductImage.objects.create(
                product=product,
                image=image_data.get("image"),
                order=image_data.get("order"),
            )
            if image_obj.order == 1:
                thumbnail_url = image_obj.image

        if thumbnail_url:
            product.thumbnail = thumbnail_url
            product.save()


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

        serializer = serializers.SectionSerializer(data=request.data)
        if serializer.is_valid():
            # 동일한 제목의 섹션이 이미 있는지 확인
            if Section.objects.filter(shop_id=shop_pk, title=serializer.validated_data["title"]).exists():
                return Response(
                    {"error": "A section with this title already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 새 섹션 생성
            section = serializer.save(shop_id=shop_pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

