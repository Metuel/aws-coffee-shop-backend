from django.db import models


class ProductType(models.TextChoices):
    DRINK = 'DRINK', 'Drink'
    FOOD = 'FOOD',  'Food'
    SIDE = 'SIDE',  'Side'
    MERCH = 'MERCH', 'Merchandise'


class Size(models.TextChoices):
    NONE = '',  'N/A'
    SMALL = 'S', 'Small'
    MEDIUM = 'M', 'Medium'
    LARGE = 'L', 'Large'
    REGULAR = 'R', 'Regular'


# Simple label/value lists for the frontend
PRODUCT_TYPES = [
    {'value': v, 'label': l} for v, l in ProductType.choices
]

SIZES = [
    {'value': v, 'label': l} for v, l in Size.choices
]