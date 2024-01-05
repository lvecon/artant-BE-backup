from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


User = get_user_model()


# email authentication을 위한 class
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=email)
            )
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            # 여기서 적절한 예외 처리.
            pass


class CustomPasswordValidator:
    def validate(self, password, user=None):
        print("validator 작동")
        if len(password) < 12:
            raise ValidationError
        # 영문/숫자/특수문자 중 2가지 이상 조합 검증
        if not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)|(?=.*[A-Za-z])(?=.*[!@#$%^&*])|(?=.*\d)(?=.*[!@#$%^&*]).{8,20}$",
            password,
        ):
            raise ValidationError(
                _("비밀번호는 8~20자의 영문, 숫자, 특수문자 2가지 이상 조합이어야 합니다."),
                code="password_no_complexity",
            )

        # 3개 이상 연속되거나 동일한 문자/숫자 제외
        if re.search(r"(.)\1\1", password) or re.search(r"(\d)\1\1", password):
            raise ValidationError(
                _("비밀번호에 동일한 문자나 숫자가 3개 이상 연속될 수 없습니다."),
                code="password_too_simple",
            )

    def get_help_text(self):
        return _(
            "비밀번호는 8~20자의 영문, 숫자, 특수문자 2가지 이상 조합이어야 하며, "
            "동일한 문자나 숫자가 3개 이상 연속될 수 없습니다."
        )
