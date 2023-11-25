from django.db import models


class ProductColorChoices(models.TextChoices):
    White = ("White", "White")
    Black = ("Black", "Black")
    Blue = ("Blue", "Blue")
    Green = ("Green", "Green")
    Gray = ("Gray", "Gray")
    Orange = ("Orange", "Orange")
    Purple = ("Purple", "Purple")
    Red = ("Red", "Red")
    Brown = ("Brown", "Brown")
    Yellow = ("Yellow", "Yellow")
    Gold = ("Gold", "Gold")
    Silver = ("Silver", "Silver")
    Colorful = ("Colorful", "Colorful")
