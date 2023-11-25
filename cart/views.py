from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Count
from .models import Cart, CartLine
from products.models import (
    Product,
)
from product_variants.models import ProductVariant
from .serializers import CartSerializer, CartLineSerializer


# Create your views here.
class CartView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        cart = Cart.objects.get(user=user)

        serializer = CartSerializer(
            cart,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        product_pk = request.data.get("product_pk")
        variant_pk = request.data.get("variant_pk", None)
        quantity = int(request.data.get("quantity", 1))

        if quantity < 1:
            return Response(
                {"error": "Quantity must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(pk=product_pk, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        cart, created = Cart.objects.get_or_create(user=user)

        if variant_pk:
            try:
                variant = ProductVariant.objects.get(pk=variant_pk, product=product)
                cart_line_query = CartLine.objects.filter(
                    cart=cart, product_variant=variant
                )
            except ProductVariant.DoesNotExist:
                return Response(
                    {"error": "Invalid variant for this product."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            variant = None
            cart_line_query = CartLine.objects.filter(
                cart=cart, product=product, product_variant__isnull=True
            )

        existing_cart_line = cart_line_query.first()

        if existing_cart_line:
            existing_cart_line.quantity += quantity
            existing_cart_line.save(update_fields=["quantity"])
        else:
            CartLine.objects.create(
                cart=cart, product=product, product_variant=variant, quantity=quantity
            )

        serializer = CartLineSerializer(
            existing_cart_line
            or CartLine.objects.filter(
                cart=cart, product=product, product_variant=variant
            ).first()
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request):
        user = request.user
        cart = Cart.objects.get(user=user)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartLineView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, cartline_pk):
        cartline = CartLine.objects.get(pk=cartline_pk)

        serializer = CartLineSerializer(
            cartline,
        )
        return Response(serializer.data)

    def delete(self, request, cartline_pk):
        cartline = CartLine.objects.get(pk=cartline_pk)
        cartline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
