from django.db import models
from django.core.validators import MinValueValidator
from .choices import ProductType, Size


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category     = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    product_type = models.CharField(
        max_length=10,
        choices=ProductType.choices,
        default=ProductType.DRINK,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    size = models.CharField(
        max_length=1,
        choices=Size.choices,
        blank=True,
        default=Size.NONE,
    )

    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    contains_nuts = models.BooleanField(default=False)

    image = models.ImageField(upload_to='products/', blank=True, null=True, max_length=600)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name', 'size']
        indexes = [models.Index(fields=['product_type'])]

    def __str__(self):
        return f'{self.name} ({self.get_size_display()})' if self.size else self.name