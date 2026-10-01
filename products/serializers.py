from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'product_count']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    product_type_display = serializers.CharField(source='get_product_type_display', read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'category', 'category_name',
            'product_type', 'product_type_display',
            'name', 'description',
            'price', 'size', 'size_display',
            'is_vegetarian', 'is_vegan', 'is_gluten_free', 'contains_nuts',
            'image', 'is_available', 'is_featured', 'stock',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value