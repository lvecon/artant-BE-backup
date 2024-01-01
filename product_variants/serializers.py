from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


from .models import (
    VariationOption,
    Variation,
    ProductVariant,
)


class VariationSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = (
            "name",
            "options",
        )

    def get_options(self, obj):
        return [option.name for option in obj.options.all()]


class VariationOptionSerializer(serializers.ModelSerializer):
    variation = serializers.CharField(source="variation.name")

    class Meta:
        model = VariationOption
        fields = (
            "variation",
            "name",
        )


class ProductVariantSerializer(serializers.ModelSerializer):
    option_one = VariationOptionSerializer(read_only=True)
    option_two = VariationOptionSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = (
            "option_one",
            "option_two",
            "sku",
            "price",
            "quantity",
            "is_visible",
        )
