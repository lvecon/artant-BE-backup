from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from .models import Shop
from django.conf import settings


class ShopsViewTest(TestCase):
    URL = "/api/v1/shops/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_create_shop_success(self):
        # 성공적인 상점 생성을 테스트합니다.
        response = self.client.post(self.URL, {"shop_name": "My Test Shop"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["shop_name"], "My Test Shop")
        self.assertEqual(response.data["register_step"], 1)
        # 상점이 실제로 생성되었는지 확인합니다.
        self.assertTrue(Shop.objects.filter(shop_name="My Test Shop").exists())

    def test_duplicate_shop_creation(self):
        self.client.post(self.URL, {"shop_name": "My Test Shop"})
        # 동일한 사용자가 두 번째 상점을 생성하려고 시도합니다.
        response = self.client.post(self.URL, {"shop_name": "My Second Test Shop"})
        self.assertEqual(response.status_code, 400)
        # 중복 상점 생성 오류 메시지를 확인합니다.
        self.assertEqual(response.data["error"], "You already have a shop.")

    def test_create_shop_without_name(self):
        # 상점 이름 없이 상점을 생성하려고 시도합니다.
        response = self.client.post(self.URL, {})
        self.assertEqual(response.status_code, 400)
        # 필수 필드 누락 오류를 확인합니다.
        self.assertIn("shop_name", response.data)


class ShopDetailViewTest(TestCase):
    URL = "/api/v1/shops/"

    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="testpass")
        self.other_user = User.objects.create_user(
            username="user2", password="testpass"
        )
        self.shop = Shop.objects.create(user=self.user, shop_name="Test Shop")
        self.client.login(username="user1", password="testpass")

    def test_get_shop_detail(self):
        response = self.client.get(reverse("shop_detail", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["shop_name"], self.shop.shop_name)

    def test_patch_shop_detail(self):
        updated_data = {"shop_name": "Updated Shop"}
        response = self.client.patch(
            reverse("shop_detail", kwargs={"pk": self.shop.pk}), updated_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.shop.refresh_from_db()
        self.assertEqual(self.shop.shop_name, "Updated Shop")

    def test_patch_shop_detail_permission_denied(self):
        self.client.logout()
        self.client.login(username="user2", password="testpass")
        updated_data = {"shop_name": "Unauthorized Update"}
        response = self.client.patch(
            reverse("shop_detail", kwargs={"pk": self.shop.pk}), updated_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_shop(self):
        response = self.client.delete(
            reverse("shop_detail", kwargs={"pk": self.shop.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Shop.objects.filter(pk=self.shop.pk).exists())


class ShopBannersViewTest(TestCase):
    URL = "/api/v1/shops/banners"

    def setUp(self):
        # Setup test data for shops
        for i in range(16):
            user = User.objects.create(
                username=f"user{i}", email=f"example{i}@gmail.com", password="test"
            )
            Shop.objects.create(
                user=user,
                shop_name=f"Shop {i}",
                background_pic=f"http://example{i}.com/pic.jpg" if i % 2 == 0 else None,
            )

    def test_shop_banners(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) <= settings.SHOP_BANNER_PAGE_SIZE)
        self.assertTrue(
            all(
                "background_pic" in shop and shop["background_pic"] is not None
                for shop in response.data
            )
        )


class FeaturedShopsViewTest(TestCase):
    URL = "/api/v1/shops/featured-shops"

    def setUp(self):
        # Setup test data for shops
        for i in range(10):
            user = User.objects.create(
                username=f"user{i}", email=f"example{i}@gmail.com", password="test"
            )
            Shop.objects.create(
                user=user,
                shop_name=f"Shop {i}",
                avatar="http://example.com/avatar.jpg" if i % 2 == 0 else None,
            )

    def test_featured_shops(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) <= settings.FEATURED_SHOP_PAGE_SIZE)
        self.assertTrue(
            all(
                "avatar" in shop and shop["avatar"] is not None
                for shop in response.data
            )
        )
