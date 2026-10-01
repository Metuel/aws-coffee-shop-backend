from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("subtotal",)

    @admin.display(description="Subtotal")
    def subtotal(self, obj):
        return obj.subtotal if obj.pk else "-"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total", "updated_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "subtotal")
    search_fields = ("cart__user__username", "product__name")

    @admin.display(description="Subtotal")
    def subtotal(self, obj):
        return obj.subtotal