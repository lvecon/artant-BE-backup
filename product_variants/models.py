from django.db import models


class Variation(models.Model):
    name = models.CharField(max_length=32)
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="variations"
    )
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} : {self.product.name}"


class VariationOption(models.Model):
    name = models.CharField(max_length=32)
    variation = models.ForeignKey(
        Variation, on_delete=models.CASCADE, related_name="options"
    )
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.variation.name} - {self.name} : {self.variation.product.name}"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="variants"
    )
    option_one = models.ForeignKey(
        VariationOption,
        on_delete=models.CASCADE,
        related_name="variants_as_option_one",
        null=True,
        blank=True,
    )
    option_two = models.ForeignKey(
        VariationOption,
        on_delete=models.CASCADE,
        related_name="variants_as_option_two",
        null=True,
        blank=True,
    )
    sku = models.CharField(max_length=255, null=True, blank=True)
    price = models.PositiveIntegerField(null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    order = models.PositiveIntegerField()

    def __str__(self):
        options = filter(None, [self.option_one, self.option_two])
        option_descriptions = " x ".join(option.name for option in options)
        return f"{self.product.name} - {option_descriptions}"
