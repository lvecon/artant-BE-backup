from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Count
from .models import Cart, CartLine
from products.models import Product, VariantValue
from .serializers import CartSerializer, CartLineSerializer


# Create your views here.
class CartView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user)

        serializer = CartSerializer(
            cart,
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        product_pk = request.data.get("product_pk")
        variant_pks = request.data.get("variant_pks", [])
        quantity = request.data.get("quantity", 1)

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

        existing_cart_line = (
            CartLine.objects.filter(
                cart__user=user,
                product=product,
                variant__in=variants,
            )
            .annotate(matched_variants=Count("variant"))
            .filter(matched_variants=len(variants))
            .first()
        )

        if existing_cart_line:
            # If an existing cart line exists, update the quantity
            existing_cart_line.quantity += quantity
            existing_cart_line.save()
            serializer = CartLineSerializer(existing_cart_line)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # If no existing cart line, create a new one
            cart_line = CartLine(
                cart=Cart.objects.get(user=user),
                product=product,
                quantity=quantity,
            )
            cart_line.save()
            cart_line.variant.set(variants)
            serializer = CartLineSerializer(cart_line)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        pass


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
