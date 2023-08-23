from django.conf import settings
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status

from rest_framework.response import Response
from .serializers import EventSerializer
from .models import Event


# Create your views here.
class Events(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        events = Event.objects.order_by("-created_at")
        serializer = EventSerializer(
            events[start:end],
            many=True,
        )

        return Response(serializer.data)
