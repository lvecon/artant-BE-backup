import json
from config.settings import CORPORATE_API_KEY
import jwt
import re
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email, ValidationError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated
from users.models import User
from . import serializers
from .utils import check_phone_number


class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # print("Hi", request.headers)
        request.session["init"] = True
        request.session.save()

        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
    # 비회원으로 최근에 본 상품들을 로그인하면서 db에 넣어줘야 할지?
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        rememberMe = request.data.get("rememberMe")

        if not email or not password:
            raise ParseError("Email and password are required")

        # Authenticate user based on email. 보안상 유저 존재 여부와 관련 없이 로그인 실패 시 항상 같은 에러
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            if rememberMe:
                # Set session to expire after a longer period (e.g., 2 weeks)
                request.session.set_expiry(1209600)  # 2 weeks, in seconds
            else:
                # Session will expire when the user closes the browser
                request.session.set_expiry(0)

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
        print(request.data)
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


class CorporateNumberCheck(APIView):
    # 설명은 https://www.data.go.kr/data/15081808/openapi.do
    def post(self, request):
        corporate_number = request.data.get("corporate_number")
        print(corporate_number)
        headers = {"Content-type": "application/json; charset=utf-8"}
        url = f"http://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey={CORPORATE_API_KEY}&returnType=JSON"
        data = {"b_no": [corporate_number]}
        print(data)
        response = requests.post(url, headers=headers, data=json.dumps(data))
        res = response.json()
        try:
            if res["match_cnt"] == 1:
                return Response(
                    {"message": "Corporate Number is available"},
                    status=status.HTTP_200_OK,
                )
        except:
            return Response(
                {"message": "Corporate Number is unavailable"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
        result = check_phone_number(phone_number)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


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


class PasswordResetRequestView(APIView):
    def post(self, request):
        name = request.data.get("name")
        email = request.data.get("email")

        if not name or not email:
            return Response(
                {"error": "Name and email are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.send_reset_email(name, email):
            return Response(
                {"message": "Password reset email sent."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def send_reset_email(self, name, email):
        # 사용자를 이름과 이메일로 찾습니다.
        try:
            user = User.objects.get(name=name, email=email)
        except User.DoesNotExist:
            return False

        # 토큰과 UID 생성 TODO: 기본 토큰 만료시간 24시간. 보안 강화 위해 변경 고려.
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # 비밀번호 재설정 URL
        reset_url = f"http://example.com/reset_password?uid={uid}&token={token}"

        # 이메일 전송
        send_mail(
            "Password Reset",
            f"Please click on the link to reset your password: {reset_url}",
            "hoon40@dataant.co.kr",  # 발신자 주소를 실제 이메일 주소로 변경해야 합니다.
            [user.email],
            fail_silently=False,
        )
        return True


class PasswordResetConfirmView(APIView):
    def post(self, request, *args, **kwargs):
        # 요청에서 uid, token, new_password, confirm_password를 추출
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # 새 비밀번호와 확인 비밀번호가 일치하는지 확인
        if new_password != confirm_password:
            return Response(
                {"error": "New password and confirm password do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # uid를 사용하여 사용자 객체를 가져옴
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid token or user does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 토큰 검증 및 비밀번호 재설정
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid token or user does not exist."},
            status=status.HTTP_400_BAD_REQUEST,
        )
