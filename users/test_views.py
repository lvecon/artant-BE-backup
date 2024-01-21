from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from users.models import User
from django.contrib.auth.hashers import make_password


class MeAPITest(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성 및 인증
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            password=make_password("testpassword"),
        )
        self.client.force_authenticate(user=self.user)

    def test_get_me(self):
        # 현재 인증된 사용자 정보를 가져오는 GET 요청 테스트
        response = self.client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)

    def test_patch_me(self):
        # 사용자 정보를 업데이트하는 PATCH 요청 테스트
        new_data = {"name": "New Name", "email": "newemail@example.com"}
        response = self.client.patch("/api/v1/users/me", new_data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, "newemail@example.com")

    def test_delete_me(self):
        # 사용자를 삭제하는 DELETE 요청 테스트
        response = self.client.delete("/api/v1/users/me")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username="testuser").exists())
