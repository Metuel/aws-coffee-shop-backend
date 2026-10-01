from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'product_count')
    search_fields = ('name',)

    @admin.display(description='Products')
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'product_type', 'size',
                     'price', 'stock', 'is_available', 'is_featured')
    list_filter = ('product_type', 'category', 'size',
                     'is_available', 'is_featured',
                     'is_vegetarian', 'is_vegan', 'is_gluten_free', 'contains_nuts')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_available', 'is_featured')