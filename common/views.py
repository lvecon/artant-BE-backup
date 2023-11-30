from django.conf import settings
from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


class GetUploadURL(APIView):
    def post(self, request):
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/images/v2/direct_upload"

        one_time_url = requests.post(
            url,
            headers={"Authorization": f"Bearer {settings.CF_TOKEN}"},
        )
        one_time_url = one_time_url.json()
        result = one_time_url.get("result")
        return Response({"uploadURL": result.get("uploadURL")})


class GetVideoUploadURL(APIView):
    def post(self, request):
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/stream/direct_upload"

        payload = {"maxDurationSeconds": 60}  # TODO: maxDuration 논의 필요

        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {settings.CF_TOKEN}"},
                json=payload,  # Use json parameter to send JSON data in the request body
            )
            response_data = response.json()
            if response.status_code == 200:
                upload_url = response_data.get("result", {}).get("uploadURL")
                if upload_url:
                    return Response({"uploadURL": upload_url})
                else:
                    return Response(
                        {"error": "Failed to retrieve upload URL"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            else:
                return Response(response_data, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Request to Cloudflare failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
