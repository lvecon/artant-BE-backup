from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import User, ShippingAddress
from django.db.utils import IntegrityError


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 테스트를 위한 User 인스턴스 생성
        cls.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            name="Test User",
            gender="Male",
            cell_phone_number="01012345678",
            agreed_to_terms_of_service=True,
            agreed_to_privacy_policy=True,
            agreed_to_electronic_transactions=True,
            confirmed_age_over_14=True,
        )

    def test_email_field_unique(self):
        # 이메일 필드의 고유성 테스트
        user1 = User.objects.get(username="testuser")
        user2 = User(
            username="testuser2",
            email="testuser@example.com",  # 동일한 이메일 사용
            name="Another Test User",
            gender="Male",
            cell_phone_number="01087654321",
        )
        with self.assertRaises(IntegrityError):
            user2.save()

    def test_user_str(self):
        # __str__ 메서드 테스트
        user = User.objects.get(username="testuser")
        self.assertEqual(str(user), "Test User")

    def test_valid_email(self):
        # 유효한 이메일 주소 테스트
        user = User.objects.get(username="testuser")
        user.email = "invalid-email"
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_phone_number_length(self):
        # 전화번호 길이 검증 테스트
        user = User.objects.get(username="testuser")
        user.cell_phone_number = "12345"
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_default_shipping_address_null(self):
        # 기본 배송지 주소가 초기에는 Null인지 테스트
        self.assertIsNone(self.user.default_shipping_address)

    def test_default_payment_info_null(self):
        # 기본 결제 정보가 초기에는 Null인지 테스트
        self.assertIsNone(self.user.default_payment_info)

    def test_is_corporate_default_false(self):
        # 기본값으로 is_corporate 필드가 False인지 테스트
        self.assertFalse(self.user.is_corporate)

    def test_optional_fields_blank(self):
        # 선택적 필드(blank=True)의 기본값이 빈 문자열인지 테스트
        self.assertIsNone(self.user.avatar)
        self.assertIsNone(self.user.birthday)
        self.assertIsNone(self.user.description)

    def test_corporate_fields_when_is_corporate_true(self):
        # is_corporate가 True일 때, corporate 관련 필드들을 테스트
        self.user.is_corporate = True
        self.user.corporate_name = "Test Corp"
        self.user.corporate_number = "1234567890"
        self.user.save()

        updated_user = User.objects.get(username="testuser")
        self.assertEqual(updated_user.corporate_name, "Test Corp")
        self.assertEqual(updated_user.corporate_number, "1234567890")

    def test_agreement_fields(self):
        # 약관 동의 필드들의 기본값을 테스트
        self.assertTrue(self.user.agreed_to_terms_of_service)
        self.assertTrue(self.user.agreed_to_privacy_policy)
        self.assertTrue(self.user.agreed_to_electronic_transactions)
        self.assertTrue(self.user.confirmed_age_over_14)
        self.assertFalse(self.user.agreed_to_third_party_sharing)
        self.assertFalse(self.user.agreed_to_optional_privacy_policy)
        self.assertFalse(self.user.agreed_to_marketing_mails)


class ShippingAddressModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create(username="testuser")
        ShippingAddress.objects.create(
            user=test_user,
            recipient_name="John Doe",
            street_name_address="123 Main St",
            postal_code="12345",
            cell_phone_number="1234567890",
        )

    def test_address_str(self):
        address = ShippingAddress.objects.get(id=1)
        expected_object_name = f"{address.street_name_address}, {address.postal_code}"
        self.assertEqual(str(address), expected_object_name)

    # 추가 모델 테스트 ...
