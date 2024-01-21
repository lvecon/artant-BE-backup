from rest_framework.test import APITestCase
from rest_framework import status
from .models import User
from shops.models import Shop
import datetime


class MeViewTest(APITestCase):
    URL = "/api/v1/users/me"

    def setUp(self):
        # 사용자와 상점 인스턴스 생성
        self.user = User.objects.create_user(
            username="testUser",
            email="testUser@gmail.com",
            password="testpassword",
            name="testUser",
            gender="Male",
            birthday=datetime.date(1990, 1, 1),
            description="Initial description about the user.",
        )
        self.shop = Shop.objects.create(
            user=self.user,
            shop_name="testShop",
            avatar="https://example.com/shop_avatar.jpg",
            is_activated=True,
            register_step=4,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_user_info(self):
        # 사용자 정보 조회 테스트
        response = self.client.get(self.URL)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 여기에서 response.data를 이용하여 필드 검증
        self.assertEqual(response.data["username"], "testUser")
        self.assertEqual(response.data["email"], "testUser@gmail.com")
        self.assertEqual(response.data["shop"]["shop_name"], "testShop")
        self.assertEqual(
            response.data["description"], "Initial description about the user."
        )

    def test_update_user_info(self):
        # 사용자 정보 수정 테스트
        data = {
            "name": "UpdatedName",
            "description": "Updated description about the user.",
        }
        response = self.client.patch(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "UpdatedName")
        self.assertEqual(self.user.description, "Updated description about the user.")

    def test_delete_user(self):
        # 사용자 계정 삭제 테스트
        response = self.client.delete(self.URL)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="testUser")
