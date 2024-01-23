from products.models import Product
from rest_framework.views import APIView
from products import serializers
from .models import UserProductTimestamp
from rest_framework.response import Response


# Create your views here.
class RecentlyViewed(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            # Fetch recently viewed products for authenticated users from the database
            recently_viewed_timestamps = UserProductTimestamp.objects.filter(
                user=user.pk
            ).order_by("-timestamp")[:10]
            recently_viewed_products = [
                timestamp.product for timestamp in recently_viewed_timestamps
            ]
        else:
            # Fetch recently viewed product IDs for non-authenticated users from the session
            viewed_products = request.session.get("viewed_products", [])

            # Get the latest 10 product IDs
            product_ids = [item["product_id"] for item in viewed_products[:10]]

            # Fetch products from database
            recently_viewed_products = Product.objects.filter(id__in=product_ids)
            product_dict = {product.id: product for product in recently_viewed_products}
            recently_viewed_products = [
                product_dict[product_id]
                for product_id in product_ids
                if product_id in product_dict
            ]

        # Serialize the product data
        serializer = serializers.ProductListSerializer(
            recently_viewed_products,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
