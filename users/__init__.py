from django.db import models


class UserGenderChoices(models.TextChoices):
    Female = ("Female", "Female")
    Male = ("Male", "Male")
    RatherNotSay = ("RatherNotSay", "Rather Not Say")
    Custom = ("Custom", "Custom")
