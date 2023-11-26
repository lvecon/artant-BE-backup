from django.db import models


class ProductCreationDate(models.TextChoices):
    MADETOORDER = ("Made To Order", "Made To Order")
    Y2020S = ("2020-2023", "2020-2023")
    Y2010S = ("2010-2019", "2010-2019")
    Y2000S = ("2000-2009", "2010-2009")
    BEFORE2000 = ("Before 2000", "Before 2000")
    Y1990S = ("1990-1999", "1990-1999")
    Y1980S = ("1980-1989", "1980-1989")
    Y1970S = ("1970-1979", "1970-1979")
    Y1960S = ("1960-1969", "1960-1969")
    Y1950S = ("1950-1959", "1950-1959")
    Y1940S = ("1940-1949", "1940-1949")
    Y1930S = ("1930-1939", "1930-1939")
    Y1920S = ("1920-1929", "1920-1929")
    Y1910S = ("1910-1919", "1910-1919")
    Y1900S = ("1900-1909", "1900-1909")
    Y1800S = ("1800-1899", "1800-1899")
    Y1700S = ("1700-1799", "1790-1799")
    BEFORE1700 = ("Before 1700", "Before 1700")


class ProductMadeByChoices(models.TextChoices):
    SELF = ("I did", "I did")
    MEMBER = ("A memeber of my shop", "A memeber of my shop")
    ANOTHER = ("Another company or person", "Another company or person")


class ProductTypeChoices(models.TextChoices):
    FINISHED = ("A finished product", "A finished product")
    SUPPLY = ("A supply or tool to make things", "A supply or tool to make things")


class ProductItemTypeChoices(models.TextChoices):
    Handmade = ("Handmade", "Handmade")
    Vintage = ("Vintage", "Vintage")
