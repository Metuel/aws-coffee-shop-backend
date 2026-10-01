from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "is_available"]
    list_filter = ["is_available", "category"]
    list_editable = ["price", "stock", "is_available"]
    search_fields = ["name", "description"]
