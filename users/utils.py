import re
from .models import User


def check_phone_number(phone_number):
    if not re.match(r"^01([0-9])(\d{7,8})$", phone_number):
        return {"error": "Invalid phone number format."}

    user = User.objects.filter(cell_phone_number=phone_number).first()
    if user:
        masked_email = mask_email(user.email)
        return {
            "error": "This phone number is already in use.",
            "email": masked_email,
        }

    return {"message": "Phone number is available."}


def mask_email(email):
    local_part, domain_part = email.split("@")
    masked_local = local_part[:2] + "*" * (len(local_part) - 2)
    return f"{masked_local}@{domain_part}"
