from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import Cart
from .serializers import (
    CartSerializer,
)


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
        pass

    def delete(self, request):
        pass
