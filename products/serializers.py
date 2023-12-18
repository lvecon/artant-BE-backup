from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from favorites.models import FavoriteProduct
from .models import (
    Product,
    ProductImage,
    ProductVideo,
)
from product_variants.models import (
    ProductVariant,
)
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


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("pk", "image")


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ("pk", "video")


class ProductSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "thumbnail",
            "price",
        )


class TinyProductVariantSerializer(serializers.ModelSerializer):
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


class ProductDetailSerializer(serializers.ModelSerializer):
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
    colors = ColorSerializer(many=True, read_only=True)
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
            "is_artant_star",
            "colors",
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


class ProductListSerializer(serializers.ModelSerializer):
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
            # "is_frame_included",
            # "is_artant_choice",
            # "is_artant_star",
            # "colors",
            # "product_item_type",
            # "is_giftcard_available",
            # "is_gift_wrapping_available",
            # "is_customizable",
            "is_best_seller",
            "is_star_seller",
            "is_liked",
            "thumbnail",
            # "created_at",
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
        return obj.tags.values_list("tag", flat=True)

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


class TinyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "original_price",
            "price",
            "discount_rate",
        )


# 유효성 검사 더 구체적으로 가능하게 하기 TODO: validate method 추가
class ProductCreateSerializer(serializers.ModelSerializer):
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
        ]

    def get_primary_color(self, obj):
        return obj.primary_color.name if obj.primary_color else None

    def get_secondary_color(self, obj):
        return obj.secondary_color.name if obj.secondary_color else None

    def get_category(self, obj):
        return [category.name for category in obj.category.all()]

    def get_tags(self, obj):
        return [tag.tag for tag in obj.tags.all()]

    def get_section(self, obj):
        return obj.section.title if obj.section else None

    def get_materials(self, obj):
        return [material.name for material in obj.materials.all()]

    def get_images(self, obj):
        images = obj.images.order_by("order").values_list("image", flat=True)
        return list(images)

    def get_video(self, obj):
        return obj.video.video if hasattr(obj, "video") and obj.video else None


class ProductUpdateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True, required=False)
    primary_color = serializers.CharField(required=False, allow_null=True)
    secondary_color = serializers.CharField(required=False, allow_null=True)
    section = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # SerializerMethodField를 사용하여 읽기 전용 필드를 정의
    # variations = serializers.SerializerMethodField()
    # variants = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subCategory = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "made_by",
            "product_type",
            "product_creation_date",
            "category_name",
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
        )

    def update(self, instance, validated_data):
        # `tags` 필드는 validated_data에 포함되지 않으므로, 별도로 처리
        tags_list = self.context.get("request").data.get("tags")
        if tags_list is not None:
            instance.tags.clear()
            for tag_name in tags_list:
                tag, created = ProductTag.objects.get_or_create(tag=tag_name)
                instance.tags.add(tag)

        materials_list = self.context.get("request").data.get("materials")
        if materials_list is not None:
            instance.materials.clear()
            for material_name in materials_list:
                material, created = Material.objects.get_or_create(name=material_name)
                instance.materials.add(material)

        # 이미지 처리
        images_data = self.context.get("request").data.get("images")
        if images_data is not None:
            self.update_images(images_data, instance)

        # 비디오 처리
        video_url = self.context.get("request").data.get("video")
        if video_url is not None:
            if video_url == "" and hasattr(instance, "video"):
                # 비디오 URL이 빈 문자열이고 상품에 비디오가 있는 경우, 비디오 삭제
                instance.video.delete()
            elif video_url:
                # 비디오 URL이 존재하면 기존 비디오 업데이트 또는 새 비디오 생성
                if hasattr(instance, "video"):
                    instance.video.video = video_url
                    instance.video.save()
                else:
                    ProductVideo.objects.create(video=video_url, product=instance)

        # ----- validated_data 사용 ------
        # category_name 처리
        category_name = validated_data.pop("category_name", None)
        if category_name:
            category = get_object_or_404(Category, name=category_name)
            instance.category.clear()
            instance.category.add(category)
            # 상위 카테고리 추가 (필요한 경우)
            if category.parent:
                instance.category.add(category.parent)

        # primary_color 처리
        primary_color_name = validated_data.pop("primary_color", None)
        if primary_color_name is not None:
            primary_color = Color.objects.filter(name=primary_color_name).first()
            if primary_color:
                instance.primary_color = primary_color
            else:
                raise serializers.ValidationError(
                    {"primary_color": "Invalid color name"}
                )

        # secondary_color 처리
        secondary_color_name = validated_data.pop("secondary_color", None)
        if secondary_color_name is not None:
            secondary_color = Color.objects.filter(name=secondary_color_name).first()
            if secondary_color:
                instance.secondary_color = secondary_color
            else:
                raise serializers.ValidationError(
                    {"secondary_color": "Invalid color name"}
                )

        # section 처리
        section_name = validated_data.pop("section", None)
        if section_name is not None:
            if section_name.strip():  # 빈 문자열이 아닌 경우
                # 상점에 해당하는 섹션을 찾거나 생성
                section_instance, created = Section.objects.get_or_create(
                    title=section_name, shop=instance.shop
                )
                if created:  # 새로운 섹션이 생성된 경우
                    # 현재 상점의 섹션 개수를 기준으로 order 값을 설정
                    last_order = Section.objects.filter(shop=instance.shop).count()
                    section_instance.order = last_order
                    section_instance.save()
                # 섹션을 상품과 연결
                instance.section = section_instance
            else:
                # 섹션 연결 제거 (빈 문자열인 경우)
                instance.section = None

        # 나머지 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def get_category(self, product):
        return product.category.get(level=2).name

    def get_subCategory(self, product):
        return product.category.get(level=3).name

    def get_tags(self, obj):
        return [tag.tag for tag in obj.tags.all()]

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

    def update_images(self, images_data, product):
        existing_images = set(product.images.all())
        updated_images = set()

        for index, image_data in enumerate(images_data, start=1):
            image_id = image_data.get("id")
            image_order = index
            if image_id:
                # 기존 이미지 업데이트
                image = product.images.get(id=image_id)
                for key, value in image_data.items():
                    if key != "order":
                        setattr(image, key, value)
                image.order = image_order
                image.save()
                updated_images.add(image)
            else:
                # 새 이미지 추가
                image_data["order"] = image_order
                new_image = ProductImage.objects.create(**image_data, product=product)
                updated_images.add(new_image)

        # 삭제되어야 하는 이미지 찾기 및 삭제
        for image in existing_images - updated_images:
            image.delete()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "order"]
