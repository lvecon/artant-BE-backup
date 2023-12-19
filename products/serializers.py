from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.db import transaction
from django.db.models import Max
from favorites.models import FavoriteProduct
from .models import (
    Product,
    ProductImage,
    ProductVideo,
)
from product_variants.models import ProductVariant, Variation, VariationOption
from product_attributes.models import Category, Color, ProductTag, Material
from shops.models import Section
from datetime import datetime, timedelta
from users.serializers import TinyUserSerializer
from product_variants.serializers import (
    VariationSerializer,
    VariationOptionSerializer,
    ProductVariantSerializer,
)
from product_attributes.serializers import ColorSerializer
from cart.models import CartLine


class ImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("pk", "image")


class VideoSerializer(ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ("pk", "video")


class ProductSnapshotSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "thumbnail",
            "price",
        )


class TinyProductVariantSerializer(ModelSerializer):
    option_one = VariationOptionSerializer(read_only=True)
    option_two = VariationOptionSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = (
            "pk",
            "price",
            "option_one",
            "option_two",
        )


# TODO: images, video 보다 간략하게 수정하기.
class ProductDetailSerializer(ModelSerializer):
    rating = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_star_seller = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subCategory = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    shop_pk = serializers.SerializerMethodField()
    shop_avatar = serializers.SerializerMethodField()

    shop_owner = serializers.SerializerMethodField()
    shipping_date = serializers.SerializerMethodField()
    cart_count = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)
    video = VideoSerializer()
    primary_color = serializers.SerializerMethodField()
    secondary_color = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()

    options = serializers.SerializerMethodField()
    separate_options = serializers.SerializerMethodField()

    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "shop_pk",
            "shop_name",
            "shop_avatar",
            "shop_owner",
            "original_price",
            "price",
            "discount_rate",
            "rating",
            "rating_count",
            "cart_count",
            "quantity",
            "shipping_price",
            "is_free_shipping",
            "processing_min",
            "processing_max",
            "shipping_date",
            "is_return_exchange_available",
            "is_frame_included",
            "is_artant_choice",
            "product_item_type",
            "is_giftcard_available",
            "is_gift_wrapping_available",
            "is_customizable",
            "images",
            "video",
            "is_best_seller",
            "is_star_seller",
            "is_liked",
            "thumbnail",
            "created_at",
            "category",
            "subCategory",
            # "options",
            "item_width",
            "item_height",
            "primary_color",
            "secondary_color",
            "materials",
            "description",
            "options",
            "separate_options",
        )

    def get_rating(self, product):
        return product.rating()

    def get_is_liked(self, product):
        request = self.context.get("request")
        if request:
            if request.user.is_authenticated:
                return FavoriteProduct.objects.filter(
                    user=request.user,
                    products__pk=product.pk,
                ).exists()
        return False

    def get_category(self, product):
        return product.category.get(level=2).name

    def get_subCategory(self, product):
        return product.category.get(level=3).name

    def get_shop_name(self, product):
        return product.shop.shop_name

    def get_shop_avatar(self, product):
        return product.shop.avatar

    def get_shop_pk(self, product):
        return product.shop.pk

    def get_shop_owner(self, product):
        user = product.shop.user
        serializer = TinyUserSerializer(user)
        return serializer.data

    def get_is_star_seller(self, product):
        return product.shop.is_star_seller

    def get_shipping_date(self, product):
        today = datetime.now().date()  # 현재 날짜
        processing_min = int(product.processing_min)  # 최소 처리 기간
        processing_max = int(product.processing_max)  # 최대 처리 기간

        min_shipping_date = today + timedelta(days=processing_min)
        max_shipping_date = today + timedelta(days=processing_max)

        return f"{min_shipping_date.month}월 {min_shipping_date.day}일 ~ {max_shipping_date.month}월 {max_shipping_date.day}일"

    def get_cart_count(self, product):
        count_in_carts = CartLine.objects.filter(
            product=product,
        ).count()

        return count_in_carts

    def get_primary_color(self, obj):
        return obj.primary_color.name if obj.primary_color else None

    def get_secondary_color(self, obj):
        return obj.secondary_color.name if obj.secondary_color else None

    def get_materials(self, obj):
        return [material.name for material in obj.materials.all()]

    def get_options(self, product):
        options_list = []
        for variant in product.variants.all():
            option_labels = []
            if variant.option_one:
                option_labels.append(variant.option_one.name)
            if variant.option_two:
                option_labels.append(variant.option_two.name)

            price = f"{variant.price:,}원" if variant.price else ""
            option_str = "x".join(option_labels) + (f" ({price})" if price else "")
            options_list.append(option_str)

        return options_list

    def get_separate_options(self, product):
        separate_options_dict = {}
        for variation in product.variations.all():
            # 여기서 'options'는 Variation 모델의 related_name으로 설정된 필드명을 사용해야 합니다.
            # 이 예에서는 Variation 모델에 related_name='options'로 설정되어 있다고 가정합니다.
            options = variation.options.all()
            option_names = [option.name for option in options if option.name]
            if option_names:
                separate_options_dict[variation.name] = option_names

        # 각각의 옵션 카테고리별로 집합을 리스트 형태로 변환
        return [{key: value} for key, value in separate_options_dict.items()]

    def get_rating(self, product):
        count = product.reviews.count()
        if count == 0:
            return 0
        else:
            total_rating = 0
            for review in product.reviews.all().values("rating"):
                total_rating += review["rating"]
            return round(total_rating / count, 2)

    def get_rating_count(self, product):
        return product.reviews.count()


class ProductListSerializer(ModelSerializer):
    rating = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    is_star_seller = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    # colors = ColorSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "shop_name",
            "original_price",
            "price",
            "discount_rate",
            "rating",
            "rating_count",
            "is_free_shipping",
            "is_discount",
            "tags",
            "is_best_seller",
            "is_star_seller",
            "is_liked",
            "thumbnail",
            "category",
        )

    def get_rating(self, product):
        return product.rating()

    def get_is_liked(self, product):
        request = self.context.get("request")

        if request:
            if request.user.is_authenticated:
                return FavoriteProduct.objects.filter(
                    user=request.user,
                    products__pk=product.pk,  # 이 부분을 수정하여 products 필드의 pk를 확인합니다.
                ).exists()
        return False

    def get_category(self, product):
        return product.category.get(level=2).name

    def get_shop_name(self, product):
        return product.shop.shop_name

    def get_tags(self, obj):
        return obj.tags.values_list("name", flat=True)

    def get_is_star_seller(self, product):
        return product.shop.is_star_seller

    def get_rating(self, product):
        count = product.reviews.count()
        if count == 0:
            return 0
        else:
            total_rating = 0
            for review in product.reviews.all().values("rating"):
                total_rating += review["rating"]
            return round(total_rating / count, 2)

    def get_rating_count(self, product):
        return product.reviews.count()


class TinyProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "original_price",
            "price",
            "discount_rate",
        )


# TODO: Variation 기획 변경으로 모델 및 관련 로직 전면 수정
class ProductCreateSerializer(ModelSerializer):
    primary_color = serializers.SerializerMethodField()
    secondary_color = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    variations = VariationSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    thumbnail = serializers.URLField(read_only=True)

    # 쓰기 전용 필드
    category_name_input = serializers.CharField(write_only=True)
    primary_color_input = serializers.CharField(write_only=True, required=False)
    secondary_color_input = serializers.CharField(write_only=True, required=False)
    tags_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    section_input = serializers.CharField(
        write_only=True, allow_blank=True, required=False
    )
    materials_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    images_input = serializers.ListField(child=serializers.URLField(), write_only=True)
    video_input = serializers.CharField(
        write_only=True, allow_blank=True, required=False
    )
    # variations_input = serializers.ListField(
    #     child=serializers.DictField(), write_only=True, required=False
    # )
    # variants_input = serializers.ListField(
    #     child=serializers.DictField(), write_only=True, required=False
    # )

    class Meta:
        model = Product
        fields = [
            "id",
            "shop",
            "name",
            "made_by",
            "product_type",
            "product_creation_date",
            "category",
            "primary_color",
            "secondary_color",
            "tags",
            "section",
            "materials",
            "description",
            "price",
            "quantity",
            "sku",
            "thumbnail",
            "images",
            "video",
            "processing_min",
            "processing_max",
            "shipping_price",
            "is_personalization_enabled",
            "is_personalization_optional",
            "personalization_guide",
            "variations",
            "variants",
            # 쓰기 전용 필드
            "category_name_input",
            "primary_color_input",
            "secondary_color_input",
            "tags_input",
            "section_input",
            "materials_input",
            "images_input",
            "video_input",
            # "variations_input",
            # "variants_input",
        ]

    def get_primary_color(self, obj):
        return obj.primary_color.name if obj.primary_color else None

    def get_secondary_color(self, obj):
        return obj.secondary_color.name if obj.secondary_color else None

    def get_category(self, obj):
        return [category.name for category in obj.category.all()]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_section(self, obj):
        return obj.section.title if obj.section else None

    def get_materials(self, obj):
        return [material.name for material in obj.materials.all()]

    def get_images(self, obj):
        images = obj.images.order_by("order").values_list("image", flat=True)
        return list(images)

    def get_video(self, obj):
        return obj.video.video if hasattr(obj, "video") and obj.video else None

    def create(self, validated_data):
        # 사용자 정의 필드 처리
        shop_pk = validated_data.get("shop")
        category_name = validated_data.pop("category_name_input")
        primary_color_name = validated_data.pop("primary_color_input", None)
        secondary_color_name = validated_data.pop("secondary_color_input", None)
        tags_data = validated_data.pop("tags_input", [])
        section_title = validated_data.pop("section_input", None)
        materials_data = validated_data.pop("materials_input", [])
        images_data = validated_data.pop("images_input", [])
        video_url = validated_data.pop("video_input", None)
        # variations_data = validated_data.pop("variations_input", [])
        # variants_data = validated_data.pop("variants_input", [])

        with transaction.atomic():  # 트랜잭션 시작. 추가 필드 처리에서 에러 발생 시 상품 생성 방지
            # 상품 객체 생성
            product = Product.objects.create(**validated_data)

            # 추가 필드 처리
            self.set_category(product, category_name)
            self.set_colors(product, primary_color_name, secondary_color_name)
            self.set_section(product, section_title, shop_pk)
            self.set_materials(product, materials_data)
            self.set_tags(product, tags_data)
            self.process_images(product, images_data)
            self.create_video(product, video_url)

            return product

    def set_category(self, product, category_name):
        if category_name:
            category = Category.objects.get(name=category_name)
            product.category.add(category)
            if category.parent:
                product.category.add(category.parent)

    def set_colors(self, product, primary_color_name, secondary_color_name):
        if primary_color_name:
            primary_color = Color.objects.get(name=primary_color_name)
            product.primary_color = primary_color
        if secondary_color_name:
            secondary_color = Color.objects.get(name=secondary_color_name)
            product.secondary_color = secondary_color
        product.save()

    def set_section(self, product, section_title, shop_pk):
        if section_title:
            section, created = Section.objects.get_or_create(
                title=section_title, shop_id=shop_pk
            )
            if created:
                max_order = (
                    Section.objects.filter(shop_id=shop_pk).aggregate(Max("order"))[
                        "order__max"
                    ]
                    or 0
                )
                section.order = max_order + 1
                section.save()
            product.section = section
            product.save()
            product.save()

    def set_materials(self, product, materials_data):
        for material_name in materials_data:
            material, _ = Material.objects.get_or_create(name=material_name)
            product.materials.add(material)

    def set_tags(self, product, tags_data):
        for tag_name in tags_data:
            tag, _ = ProductTag.objects.get_or_create(name=tag_name)
            product.tags.add(tag)

    def process_images(self, product, images_data):
        for index, image_url in enumerate(images_data, start=1):
            ProductImage.objects.create(product=product, image=image_url, order=index)
            if index == 1:
                product.thumbnail = image_url
                product.save()

    def create_video(self, product, video_url):
        if video_url:
            ProductVideo.objects.create(product=product, video=video_url)

    # def create_variations(self, product, variations_data):
    #     for index, variation_data in enumerate(variations_data, start=1):
    #         variation = Variation.objects.create(
    #             product=product,
    #             name=variation_data["name"],
    #             is_sku_vary=variation_data["is_sku_vary"],
    #             is_price_vary=variation_data.get("is_price_vary", False),
    #             is_quantity_vary=variation_data.get("is_quantity_vary", False),
    #             order=index,
    #         )
    #         self.create_variation_options(variation, variation_data.get("options", []))

    # def create_variation_options(self, variation, options_data):
    #     for index, option_data in enumerate(options_data, start=1):
    #         VariationOption.objects.create(
    #             variation=variation,
    #             name=option_data["name"],
    #             order=index,
    #         )

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


# 상품 정보 수정
class ProductUpdateSerializer(ModelSerializer):
    # SerializerMethodField를 사용하여 읽기 전용 필드를 정의
    # variations = serializers.SerializerMethodField()
    # variants = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subCategory = serializers.SerializerMethodField()
    primary_color = serializers.SerializerMethodField()
    secondary_color = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

    # 쓰기 전용 필드
    category_name_input = serializers.CharField(write_only=True, required=False)
    primary_color_input = serializers.CharField(write_only=True, required=False)
    secondary_color_input = serializers.CharField(write_only=True, required=False)
    tags_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    section_input = serializers.CharField(write_only=True, required=False)
    materials_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    images_input = serializers.ListField(
        child=serializers.JSONField(), write_only=True, required=False
    )
    video_input = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "made_by",
            "product_type",
            "product_creation_date",
            "category",
            "subCategory",
            "primary_color",
            "secondary_color",
            "tags",
            "section",
            "materials",
            "description",
            "price",
            "quantity",
            "sku",
            "processing_min",
            "processing_max",
            "shipping_price",
            "images",
            "video",
            "is_personalization_enabled",
            "is_personalization_optional",
            "personalization_guide",
            "variations",
            "variants",
            # 쓰기 전용 필드
            "category_name_input",
            "primary_color_input",
            "secondary_color_input",
            "section_input",
            "tags_input",
            "materials_input",
            "images_input",
            "video_input",
        )

    def update(self, instance, validated_data):
        # 사용자 정의 필드 처리
        with transaction.atomic():
            # 카테고리, 색상, 섹션, 태그, 소재, 이미지, 비디오 처리
            self.handle_custom_fields(instance, validated_data)

            # 나머지 필드 업데이트
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            return instance

    def handle_custom_fields(self, instance, validated_data):
        # 각 필드 처리 메소드 호출
        self.handle_category(instance, validated_data.pop("category_name_input", None))
        self.handle_colors(
            instance,
            validated_data.pop("primary_color_input", None),
            validated_data.pop("secondary_color_input", None),
        )
        self.handle_section(instance, validated_data.pop("section_input", None))
        self.handle_tags(instance, validated_data.pop("tags_input", []))
        self.handle_materials(instance, validated_data.pop("materials_input", []))
        self.handle_images(instance, validated_data.pop("images_input", []))
        self.handle_video(instance, validated_data.pop("video_input", None))

    def handle_category(self, instance, category_name):
        if category_name:
            category = Category.objects.get(name=category_name)
            instance.category.clear()
            instance.category.add(category)
            if category.parent:
                instance.category.add(category.parent)

    def handle_colors(self, instance, primary_color_name, secondary_color_name):
        if primary_color_name:
            primary_color = Color.objects.get(name=primary_color_name)
            instance.primary_color = primary_color
        if secondary_color_name:
            secondary_color = Color.objects.get(name=secondary_color_name)
            instance.secondary_color = secondary_color
        instance.save()

    def handle_section(self, instance, section_title):
        if section_title:
            section, created = Section.objects.get_or_create(
                title=section_title, shop=instance.shop
            )
            if created:  # 새로운 섹션이 생성된 경우
                # 현재 상점의 섹션 개수를 기준으로 order 값을 설정
                last_order = Section.objects.filter(shop=instance.shop).count()
                section.order = last_order
                section.save()
            instance.section = section
            instance.save()

    def handle_tags(self, instance, tags_list):
        instance.tags.clear()
        for tag_name in tags_list:
            tag, created = ProductTag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)

    def handle_materials(self, instance, materials_list):
        instance.materials.clear()
        for material_name in materials_list:
            material, created = Material.objects.get_or_create(name=material_name)
            instance.materials.add(material)

    def handle_images(self, instance, images_list):
        existing_images = set(instance.images.all())
        updated_images = set()

        for index, image_data in enumerate(images_list, start=1):
            image_id = image_data.get("id")
            image_order = index
            if image_id:
                # 기존 이미지 업데이트
                image = instance.images.get(id=image_id)
                for key, value in image_data.items():
                    if key != "order":
                        setattr(image, key, value)
                image.order = image_order
                image.save()
                updated_images.add(image)
            else:
                # 새 이미지 추가
                image_data["order"] = image_order
                new_image = ProductImage.objects.create(
                    image=image_data.get("image"), product=instance, order=image_order
                )
                updated_images.add(new_image)

        # 삭제되어야 하는 이미지 찾기 및 삭제
        for image in existing_images - updated_images:
            image.delete()

    def handle_video(self, instance, video_url):
        if video_url:
            if hasattr(instance, "video"):
                instance.video.video = video_url
                instance.video.save()
            else:
                ProductVideo.objects.create(product=instance, video=video_url)
        elif hasattr(instance, "video"):
            instance.video.delete()

    def get_category(self, product):
        return product.category.get(level=2).name

    def get_subCategory(self, product):
        return product.category.get(level=3).name

    def get_primary_color(self, obj):
        return obj.primary_color.name if obj.primary_color else None

    def get_secondary_color(self, obj):
        return obj.secondary_color.name if obj.secondary_color else None

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_section(self, obj):
        return obj.section.title if obj.section else None

    def get_materials(self, obj):
        return [material.name for material in obj.materials.all()]

    def get_images(self, shop):
        images = shop.images.order_by("order")
        return [
            {
                "id": image.pk,
                "image": image.image,
                "order": image.order,
            }
            for image in images
        ]

    def get_video(self, obj):
        return obj.video.video if hasattr(obj, "video") and obj.video else None


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "order"]
