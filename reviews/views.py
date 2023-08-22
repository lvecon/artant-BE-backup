from time import sleep
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated


from reviews.models import Review
from . import serializers
from reviews.serializers import ReviewDetailSerializer


# Create your views here.


class ReviewDetails(APIView):
    def get_object(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        review = self.get_object(pk)

        serializer = ReviewDetailSerializer(
            review,
            context={"request": request},
        )
        return Response(serializer.data)

    def delete(self, request, pk, review_pk):
        review = self.get_object(review_pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
