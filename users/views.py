import jwt
import re
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated
from users.models import User
from . import serializers


class Me(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # print("Hi", request.headers)
        print(request.user)
        user = request.user
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(
            user,
            data=request.data,
            partial=True,  # 부분 업데이트 허용
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializers.PrivateUserSerializer(user).data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


# 세션 기반 authentication
class LogIn(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise ParseError("Email and password are required")

        # Authenticate user based on email. 보안상 유저 존재 여부와 관련 없이 로그인 실패 시 항상 같은 에러
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return Response({"ok": "Welcome!"})
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# JWT-Token 기반 인증. TODO: 토큰 만료 시간 설정하기. 유저가 활동 중인 경우 만료 시간 자동갱신 기능 고려하기.
# class JWTLogIn(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")
#         if not email or not password:
#             raise ParseError
#         user = authenticate(
#             request,
#             email=email,
#             password=password,
#         )
#         if user:
#             # JWT 토큰에 유효기간 설정
#             exp_time = datetime.utcnow() + timedelta(hours=1)  # 1시간 후 만료
#             token = jwt.encode(
#                 {"pk": user.pk, "exp": exp_time},
#                 settings.SECRET_KEY,
#                 algorithm="HS256",
#             )
#             return Response({"token": token})
#         else:
#             return Response({"error": "wrong password"})


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": "bye!"})


class SignUp(APIView):
    # TODO: 필수 약관 동의 여부 확인 로직
    def post(self, request, format=None):
        serializer = serializers.UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise ParseError
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(
                {"ok": "password changed successfully!"}, status=status.HTTP_200_OK
            )
        else:
            raise ParseError


class PublicUser(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound
        serializer = serializers.PublicUserSerializer(user)
        return Response(serializer.data)


class EmailCheck(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "This email is already in use."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Email is available."}, status=status.HTTP_200_OK)


class PhoneNumberCheck(APIView):
    def post(self, request):
        phone_number = request.data.get("cell_phone_number")
        if not re.match(r"^01([0-9])(\d{7,8})$", phone_number):
            return Response(
                {"error": "Invalid phone number format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(cell_phone_number=phone_number).first()
        if user:
            masked_email = self.mask_email(user.email)
            return Response(
                {
                    "error": "This phone number is already in use.",
                    "email": masked_email,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Phone number is available."}, status=status.HTTP_200_OK
        )

    def mask_email(self, email):
        local_part, domain_part = email.split("@")
        masked_local = local_part[:2] + "*" * (len(local_part) - 2)
        return f"{masked_local}@{domain_part}"


class KakaoLogIn(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")
            access_token = requests.post(
                "https://kauth.kakao.com/oauth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": "08257a5e580b5be1b9a8785b4f4ace12",
                    "redirect_uri": "https://artant.shop",
                    "code": code,
                },
            )
            print(access_token.json())
            access_token = access_token.json().get("access_token")
            user_data = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            user_data = user_data.json()
            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")
            try:
                user = User.objects.get(email=kakao_account.get("email"))
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    email=kakao_account.get("email"),
                    username=profile.get("nickname"),
                    name=profile.get("nickname"),
                    avatar=profile.get("profile_image_url"),
                )
                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
