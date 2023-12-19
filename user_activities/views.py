from rest_framework.views import APIView
from products import serializers
from .models import UserProductTimestamp
from rest_framework.response import Response


# Create your views here.
class RecentlyViewed(APIView):
    def get(self, request):
        user = request.user
        recently_viewed_timestamps = UserProductTimestamp.objects.filter(
            user=user.pk
        ).order_by("-timestamp")[:10]
        recently_viewed_products = [
            timestamp.product for timestamp in recently_viewed_timestamps
        ]

        serializer = serializers.ProductListSerializer(
            recently_viewed_products,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
