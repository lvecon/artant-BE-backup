from time import sleep
from django.db.models import Count
from django.db.models import F
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Max
from shops.models import Shop, Section, ShopImage, ShopVideo
from products.models import Product, Color, ProductImage, ProductVideo
from product_attributes.models import Category, Material, ProductTag
from product_variants.models import ProductVariant, Variation, VariationOption
from reviews.models import Review
from . import serializers
from reviews.serializers import ReviewSerializer, ReviewDetailSerializer
from products.serializers import ProductListSerializer, ProductCreateSerializer, ProductUpdateSerializer
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
            # 이미지 정보 업데이트 (images 키가 있는 경우에만)
            if images_data is not None:
                self.update_images(images_data, shop)

            # 비디오 정보 업데이트
            video_url = request.data.get('video', None)
            if video_url is not None:
                if video_url == "" and hasattr(shop, 'video'):
                    # 비디오가 ""이고 shop에 비디오가 있는 경우, 비디오 삭제
                    shop.video.delete()
                elif video_url:
                    # 비디오 URL이 존재하면 기존 비디오 업데이트 또는 새 비디오 생성
                    if hasattr(shop, 'video'):
                        shop.video.video = video_url
                        shop.video.save()
                    else:
                        ShopVideo.objects.create(video=video_url, shop=shop)
            # 'video' 필드가 없거나 값이 None인 경우 아무것도 하지 않음


            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        shop = self.get_object(pk, request.user)
        shop.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

    def update_sections(self, sections_data, shop):
        existing_sections = set(shop.sections.all())
        updated_sections = set()

        for index, section_data in enumerate(sections_data, start=1):
            section_id = section_data.get("id")
            section_title = section_data.get("title")
            section_order = index

            if section_id:
                # 기존 섹션 업데이트
                section = shop.sections.get(id=section_id)
                for key, value in section_data.items():
                    if key != "order":  # Skip updating order from request data. TODO: is it necessary?
                        setattr(section, key, value)
                section.order = section_order 
                section.save()
                updated_sections.add(section)
            else:
                # 새 섹션 추가
                section_data["order"] = section_order
                new_section = Section.objects.create(**section_data, shop=shop)
                updated_sections.add(new_section)

        # 삭제되어야 하는 섹션 찾기 및 삭제 TODO: 삭제 허용에 대한 의논. 기존에 연결된 상품 어떻게 할지
        sections_to_delete = existing_sections - updated_sections
        for section in sections_to_delete:
            section.delete()

    def update_images(self, images_data, shop):
        existing_images = set(shop.images.all())
        updated_images = set()

        for index, image_data in enumerate(images_data, start=1):
            image_id = image_data.get("id")
            image_order = index
            if image_id:
                # 기존 이미지 업데이트
                image = shop.images.get(id=image_id)
                for key, value in image_data.items():
                    if key != "order":  # Skip updating order from request data TODO: is it necessary?
                        setattr(image, key, value)
                image.order = image_order
                image.save()
                updated_images.add(image)
            else:
                # 새 이미지 추가
                image_data["order"] = image_order
                new_image = ShopImage.objects.create(**image_data, shop=shop)
                updated_images.add(new_image)

        # 삭제되어야 하는 이미지 찾기 및 삭제
        for image in existing_images - updated_images:
            image.delete()




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
        if section_title == "모든 작품":
            # 모든 상품을 반환합니다
            pass
        elif section_title == "할인 중":
            # 할인 중인 상품만 필터링합니다 TODO: is_discount field 추가되면 수정
            products = products.filter(original_price__gt=F('price'))
        elif section_title:
            section = shop.sections.filter(title=section_title).first()
            if section:
                products = products.filter(section=section)
            else:
                return Response(
                    {"error": "section not found"}, status=status.HTTP_400_BAD_REQUEST
                )


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
        
        serializer = ProductCreateSerializer(data=data)
        if serializer.is_valid():
             # 카테고리와 색상 처리
            category = self.get_category(request)
            primary_color, secondary_color = self.get_colors(request)

            # 상품 저장
            product = serializer.save()

            # 섹션 처리 및 상품에 섹션 정보 추가
            self.set_section(data, shop_pk, product)
            
            # Variation, Variant, Material, Tag, Image
            self.create_variations(variations_data=request.data.get("variations", []), product=product)
            self.create_variants(variants_data=request.data.get("variants", []), product=product)
            self.set_materials_and_tags(materials_data=request.data.get("materials", []),
                                        tags_data=request.data.get("tags", []), product=product)
            self.process_images(images_data=request.data.get("images", []), product=product)
            self.create_video(video_url=request.data.get("video", None), product=product)
            # 카테고리, 색상 추가 및 저장
            product.category.add(category.id)
            product.primary_color = primary_color
            product.secondary_color = secondary_color
            product.save()
            # 상위 카테고리 추가
            if category.parent:
                product.category.add(category.parent.id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_category(self, request):
        category_name = request.data.get("category_name")
        category = get_object_or_404(Category, name=category_name)
        return category

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

    def set_section(self, data, shop_pk, product):
        section_title = data.get("section")
        if section_title:
            section, created = Section.objects.get_or_create(
                title=section_title, shop_id=shop_pk
            )
            if created:
                max_order = Section.objects.filter(shop_id=shop_pk).aggregate(Max('order'))['order__max'] or 0
                section.order = max_order + 1
                section.save()
            product.section = section
            product.save()
            return section

    def create_variations(self, variations_data, product):
        for index, variation_data in enumerate(variations_data, start=1):
            variation = Variation.objects.create(
                name=variation_data["name"],
                product=product,
                is_sku_vary=variation_data["is_sku_vary"],
                is_price_vary=variation_data.get("is_price_vary", False),
                is_quantity_vary=variation_data.get("is_quantity_vary", False),
                order = index,
            )
            for index, option_data in enumerate(variation_data.get("options", []), start=1):
                VariationOption.objects.create(
                    name=option_data["name"], variation=variation,  order = index,
                )

    def create_variants(self, variants_data, product):
        for index, variant_data in enumerate(variants_data, start=1):
            option_one, option_two = self.get_variant_options(variant_data, product)
            ProductVariant.objects.create(
                product=product,
                option_one=option_one,
                option_two=option_two,
                sku=variant_data.get("sku", ""),
                price=variant_data.get("price", 0),
                quantity=variant_data.get("quantity", 0),
                is_visible=variant_data.get("is_visible", True),
                order = index,
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

    def create_video(self, video_url, product):
        if video_url:
            ProductVideo.objects.create(video=video_url, product=product)


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



class ProductUpdate(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

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

        serializer = ProductUpdateSerializer(product, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    

# 상품 생성 Or 편집 화면에서 section 생성
class Sections(APIView):
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

