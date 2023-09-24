from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.conf import settings
from django.db.models import Count
from .models import Purchase, PurchaseLine
from products.models import Product, VariantValue
from .serializers import PurchaseLineSerializer, PurchaseSerializer
from datetime import datetime


# Create your views here.
class PurchaseView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.PURCHASE_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        user = request.user

        purchaselines = PurchaseLine.objects.filter(purchase__user=user)

        serializer = PurchaseLineSerializer(
            purchaselines[start:end],
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        product_pk = request.data.get("product_pk")
        variant_pks = request.data.get("variant_pks", [])
        quantity = request.data.get("quantity", 1)
        order_date = datetime.now().strftime("%Y.%m.%d")

        purchase, _ = Purchase.objects.get_or_create(user=user)

        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        # check if variant is product's variant
        if variant_pks:
            try:
                variants = VariantValue.objects.filter(
                    pk__in=variant_pks,
                    option__product=product,
                )
                if len(variant_pks) > len(variants):
                    return Response(
                        {"error": "at least one variant is not for this product."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            except VariantValue.DoesNotExist:
                return Response(
                    {"error": "Variants not found."}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            variants = []

            # If no existing purchase line, create a new one
        purchase_line = PurchaseLine(
            purchase=Purchase.objects.get(user=user),
            product=product,
            quantity=quantity,
            order_date=order_date,
        )
        purchase_line.save()
        purchase_line.variant.set(variants)
        serializer = PurchaseLineSerializer(purchase_line)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        user = request.user
        purchase = Purchase.objects.get(user=user)
        purchase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PurchaseLineView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, purchaseline_pk):
        purchaseline = PurchaseLine.objects.get(pk=purchaseline_pk)

        serializer = PurchaseLineSerializer(
            purchaseline,
        )
        return Response(serializer.data)

    def delete(self, request, purchaseline_pk):
        purchaseline = PurchaseLine.objects.get(pk=purchaseline_pk)
        purchaseline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
